import motor.motor_asyncio
from config import DB_NAME, DB_URI

class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users

    def new_user(self, id, name):
        import time
        return dict(
            id = id,
            name = name,
            session = None,
            is_premium = False,
            premium_expiry = None,
            downloads_today = 0,
            last_download_date = None,
            joined_at = time.time()
        )
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        return bool(user)
    
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        return self.col.find({})
    
    async def get_all_users_data(self):
        """Get all users with full details for export"""
        users_data = []
        cursor = self.col.find({})
        async for user in cursor:
            users_data.append({
                'user_id': user.get('id'),
                'name': user.get('name'),
                'is_premium': user.get('is_premium', False),
                'joined_at': user.get('joined_at'),
                'downloads_today': user.get('downloads_today', 0),
                'last_download_date': user.get('last_download_date')
            })
        return users_data

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def set_session(self, id, session):
        await self.col.update_one({'id': int(id)}, {'$set': {'session': session}})

    async def get_session(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('session') if user else None
    
    # Premium membership methods
    async def set_premium(self, user_id, is_premium, expiry_timestamp=None):
        """Set premium status for user"""
        await self.col.update_one(
            {'id': int(user_id)},
            {'$set': {'is_premium': is_premium, 'premium_expiry': expiry_timestamp}}
        )
    
    async def is_premium(self, user_id):
        """Check if user is premium"""
        import time
        user = await self.col.find_one({'id': int(user_id)})
        if not user:
            return False
        
        if user.get('is_premium'):
            expiry = user.get('premium_expiry')
            if expiry is None or expiry > time.time():
                return True
            else:
                # Expired, remove premium
                await self.set_premium(user_id, False, None)
                return False
        return False
    
    async def get_all_premium_users(self):
        """Get all premium users"""
        import time
        cursor = self.col.find({'is_premium': True})
        premium_users = []
        async for user in cursor:
            if user.get('premium_expiry') is None or user.get('premium_expiry') > time.time():
                premium_users.append(user)
        return premium_users
    
    # Download tracking for rate limiting
    async def check_download_limit(self, user_id, count=1):
        """Check if user can download 'count' files without exceeding limit"""
        from datetime import date
        
        user = await self.col.find_one({'id': int(user_id)})
        if not user:
            return False
        
        # Premium users have unlimited downloads
        is_premium_user = await self.is_premium(user_id)
        if is_premium_user:
            return True
        
        today = str(date.today())
        last_date = user.get('last_download_date')
        downloads_today = user.get('downloads_today', 0)
        
        # Reset if new day
        if last_date != today:
            downloads_today = 0
        
        # Check if user has enough limit left for 'count' downloads
        limit = 10  # Free users: 10/day
        return (downloads_today + count) <= limit
    
    async def increment_download_count(self, user_id):
        """Increment download count after successful download (only for non-premium)"""
        from datetime import date
        
        # Premium users don't have download limits
        is_premium_user = await self.is_premium(user_id)
        if is_premium_user:
            return
        
        user = await self.col.find_one({'id': int(user_id)})
        if not user:
            return
        
        today = str(date.today())
        last_date = user.get('last_download_date')
        downloads_today = user.get('downloads_today', 0)
        
        # Reset if new day
        if last_date != today:
            downloads_today = 0
        
        # Update count
        await self.col.update_one(
            {'id': int(user_id)},
            {'$set': {'downloads_today': downloads_today + 1, 'last_download_date': today}}
        )
    
    async def get_download_count(self, user_id):
        """Get today's download count"""
        from datetime import date
        user = await self.col.find_one({'id': int(user_id)})
        if not user:
            return 0
        
        today = str(date.today())
        if user.get('last_download_date') == today:
            return user.get('downloads_today', 0)
        return 0
    
    # Premium extension method
    async def extend_premium(self, user_id, days):
        """Extend premium membership by adding days to current expiry"""
        import time
        user = await self.col.find_one({'id': int(user_id)})
        if not user:
            return None
        
        duration = days * 24 * 60 * 60  # Convert days to seconds
        current_expiry = user.get('premium_expiry')
        
        # If user has active premium, extend from current expiry
        # Otherwise, start from now
        if current_expiry and current_expiry > time.time():
            new_expiry = current_expiry + duration
        else:
            new_expiry = time.time() + duration
        
        await self.col.update_one(
            {'id': int(user_id)},
            {'$set': {'is_premium': True, 'premium_expiry': new_expiry}}
        )
        return new_expiry
    
    # Banned users methods
    async def ban_user(self, user_id, reason, banned_by):
        """Ban a user from using the bot"""
        import time
        banned_col = self.db.banned_users
        
        # Check if already banned
        existing = await banned_col.find_one({'user_id': int(user_id)})
        if existing:
            return False  # Already banned
        
        await banned_col.insert_one({
            'user_id': int(user_id),
            'reason': reason,
            'banned_by': int(banned_by),
            'banned_at': time.time()
        })
        return True
    
    async def unban_user(self, user_id):
        """Unban a user"""
        banned_col = self.db.banned_users
        result = await banned_col.delete_one({'user_id': int(user_id)})
        return result.deleted_count > 0
    
    async def is_banned(self, user_id):
        """Check if user is banned"""
        banned_col = self.db.banned_users
        banned = await banned_col.find_one({'user_id': int(user_id)})
        return banned
    
    async def get_all_banned_users(self):
        """Get all banned users"""
        banned_col = self.db.banned_users
        banned_users = []
        cursor = banned_col.find({})
        async for user in cursor:
            banned_users.append(user)
        return banned_users

db = Database(DB_URI, DB_NAME)

