import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiocryptopay import AioCryptoPay, Networks
from database.db import db
from config import ADMINS, CRYPTO_PAY_TOKEN

# Initialize Crypto Pay client
crypto_pay = AioCryptoPay(token=CRYPTO_PAY_TOKEN, network=Networks.MAIN_NET)

# Store pending invoices: {invoice_id: {'user_id': int, 'days': int, 'amount': float, 'created_at': float}}
pending_invoices = {}

# Pricing in USD
PRICING = {
    1: {'inr': 10, 'usd': 0.15},   # 1 Day
    7: {'inr': 40, 'usd': 0.50},   # 7 Days
    30: {'inr': 100, 'usd': 1.20}  # 30 Days
}

# Background task to check invoice status
async def check_invoice_status(client: Client, invoice_id: int, user_id: int, days: int):
    """Poll invoice status and activate premium on payment"""
    max_attempts = 180  # 30 minutes (10 seconds * 180)
    attempt = 0
    
    while attempt < max_attempts:
        await asyncio.sleep(10)  # Check every 10 seconds
        attempt += 1
        
        try:
            invoices = await crypto_pay.get_invoices(invoice_ids=[invoice_id])
            if not invoices:
                continue
            
            invoice = invoices[0]
            status = invoice.status
            
            if status == 'paid':
                # Activate/extend premium
                new_expiry = await db.extend_premium(user_id, days)
                
                if new_expiry:
                    from datetime import datetime
                    expiry_date = datetime.fromtimestamp(new_expiry).strftime('%Y-%m-%d %H:%M:%S')
                    
                    try:
                        await client.send_message(
                            user_id,
                            f"""✅ **Payment Successful!**

**Premium Activated:** {days} day(s)
**Expires:** {expiry_date}

**Benefits:**
• Unlimited downloads per day
• Priority support
• Faster processing

Thank you for your purchase! 🎉
"""
                        )
                    except:
                        pass
                
                # Remove from pending
                if invoice_id in pending_invoices:
                    del pending_invoices[invoice_id]
                return
            
            elif status == 'expired':
                # Invoice expired
                try:
                    await client.send_message(
                        user_id,
                        "⏰ **Payment Expired!**\n\nYour payment invoice has expired. Please try again using /premium."
                    )
                except:
                    pass
                
                if invoice_id in pending_invoices:
                    del pending_invoices[invoice_id]
                return
        
        except Exception as e:
            print(f"Invoice check error: {e}")
            continue
    
    # Timeout - remove from pending
    if invoice_id in pending_invoices:
        del pending_invoices[invoice_id]

# Callback handler for premium purchase flow
@Client.on_callback_query(filters.regex(r"^(upgrade_premium|extend_premium|buy_|pay_)"))
async def premium_purchase_callback(client: Client, query):
    data = query.data
    user_id = query.from_user.id
    
    # Step 1: Show validity options
    if data in ["upgrade_premium", "extend_premium"]:
        buttons = [[
            InlineKeyboardButton("1 Day - ₹10/$0.15", callback_data="buy_1"),
        ],[
            InlineKeyboardButton("7 Days - ₹40/$0.50", callback_data="buy_7"),
        ],[
            InlineKeyboardButton("30 Days - ₹100/$1.20", callback_data="buy_30"),
        ],[
            InlineKeyboardButton("🔙 Back", callback_data="premium_info")
        ]]
        
        await query.message.edit_text(
            """**💎 Select Premium Duration**

Choose your preferred plan:

• **1 Day** - ₹10 / $0.15
• **7 Days** - ₹40 / $0.50  
• **30 Days** - ₹100 / $1.20

Click on a plan to continue:
""",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    
    # Step 2: Show payment method options
    elif data.startswith("buy_"):
        days = int(data.split("_")[1])
        pricing = PRICING[days]
        
        buttons = [[
            InlineKeyboardButton("💳 Pay with INR (Manual)", callback_data=f"pay_inr_{days}"),
        ],[
            InlineKeyboardButton("🪙 Pay with Crypto (Auto)", callback_data=f"pay_crypto_{days}"),
        ],[
            InlineKeyboardButton("🔙 Back", callback_data="upgrade_premium")
        ]]
        
        await query.message.edit_text(
            f"""**💳 Choose Payment Method**

**Selected Plan:** {days} Day(s)
**Price:** ₹{pricing['inr']} / ${pricing['usd']}

**Payment Options:**

💳 **INR (Manual)**
Pay via UPI and contact admin for activation.

🪙 **Crypto (Automatic)**
Instant activation via @CryptoBot.

⚠️ **Important for Crypto Payment:**
Make sure you have at least **$1** in your @CryptoBot wallet before paying. CryptoBot only accepts USDT amounts ≥$1. If you add less, you may lose your funds!
""",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    
    # Step 3a: INR Payment - Contact admin
    elif data.startswith("pay_inr_"):
        days = int(data.split("_")[2])
        pricing = PRICING[days]
        
        buttons = [[
            InlineKeyboardButton("💬 Contact Admin", url="https://t.me/tataa_sumo")
        ],[
            InlineKeyboardButton("🔙 Back", callback_data=f"buy_{days}")
        ]]
        
        await query.message.edit_text(
            f"""**💳 INR Payment**

**Plan:** {days} Day(s)
**Amount:** ₹{pricing['inr']}

**Instructions:**
1. Contact @tataa_sumo
2. Pay via UPI as directed
3. Send payment screenshot
4. Receive your redeem code
5. Use `/redeem <code>`

Click below to contact admin:
""",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    
    # Step 3b: Crypto Payment - Generate invoice
    elif data.startswith("pay_crypto_"):
        days = int(data.split("_")[2])
        pricing = PRICING[days]
        
        try:
            # Create invoice
            invoice = await crypto_pay.create_invoice(
                asset="USDT",
                amount=str(pricing['usd']),
                description=f"Premium Membership - {days} Day(s)",
                payload=f"premium_{user_id}_{days}",
                expires_in=1800  # 30 minutes
            )
            
            # Store pending invoice
            pending_invoices[invoice.invoice_id] = {
                'user_id': user_id,
                'days': days,
                'amount': pricing['usd'],
                'created_at': time.time(),
                'status': 'pending'
            }
            
            # Start background task to check payment
            asyncio.create_task(check_invoice_status(client, invoice.invoice_id, user_id, days))
            
            buttons = [[
                InlineKeyboardButton("💰 Pay Now", url=invoice.bot_invoice_url)
            ],[
                InlineKeyboardButton("🔙 Back", callback_data=f"buy_{days}")
            ]]
            
            await query.message.edit_text(
                f"""**🪙 Crypto Payment**

**Plan:** {days} Day(s)
**Amount:** ${pricing['usd']} USDT

⚠️ **IMPORTANT:**
• Make sure you have at least **$1** in your @CryptoBot wallet!
• CryptoBot only accepts USDT amounts ≥$1
• If you add less than $1, you may lose your funds!

**Instructions:**
1. Click "Pay Now" below
2. You'll be redirected to @CryptoBot
3. Complete the payment
4. Premium will be activated automatically!

**Invoice expires in:** 30 minutes
""",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        
        except Exception as e:
            await query.message.edit_text(
                f"❌ **Error creating invoice:** `{e}`\n\nPlease try again or contact @tataa_sumo.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back", callback_data=f"buy_{days}")
                ]])
            )
    
    await query.answer()

# Admin command to view crypto payments
@Client.on_message(filters.command(["cryptopayments"]) & filters.user(ADMINS))
async def view_crypto_payments(client: Client, message: Message):
    """View all pending and recent crypto invoices"""
    from datetime import datetime
    
    if not pending_invoices:
        return await message.reply("📭 **No pending crypto payments.**")
    
    text = f"**💰 PENDING CRYPTO PAYMENTS ({len(pending_invoices)})**\n\n"
    
    for inv_id, inv_data in list(pending_invoices.items())[:15]:
        user_id = inv_data['user_id']
        days = inv_data['days']
        amount = inv_data['amount']
        created = datetime.fromtimestamp(inv_data['created_at']).strftime('%H:%M:%S')
        status = inv_data.get('status', 'pending')
        
        text += f"**Invoice:** `{inv_id}`\n"
        text += f"👤 User: `{user_id}`\n"
        text += f"📅 Plan: {days} days (${amount})\n"
        text += f"⏰ Created: {created}\n"
        text += f"📊 Status: {status}\n\n"
    
    if len(pending_invoices) > 15:
        text += f"_... and {len(pending_invoices) - 15} more_"
    
    await message.reply(text)
