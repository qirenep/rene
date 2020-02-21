import aiosqlite


class ProfileNotLinked(Exception):
    pass


class ProfileAlreadyLinked(Exception):
    pass


async def link_profile(user_id, platform, name):
    """Link player profiles."""
    async with aiosqlite.connect("main.sqlite") as conn:
        try:
            await conn.execute("INSERT INTO profiles(id, platform, name) VALUES(?,?,?);",
                               (user_id, platform, name,))
            await conn.commit()
        except Exception:
            raise ProfileAlreadyLinked()


async def unlink_profile(user_id):
    """Unlink player profiles."""
    async with aiosqlite.connect("main.sqlite") as conn:
        try:
            await conn.execute("DELETE FROM profiles WHERE id=?;", (user_id,))
            await conn.commit()
        except Exception:
            raise ProfileNotLinked()


async def update_profile(user_id, platform, name):
    """Update player profiles."""
    async with aiosqlite.connect("main.sqlite") as conn:
        async with conn.execute("SELECT platform, name FROM profiles WHERE id=?;", (user_id,)) as pool:
            rows = await pool.fetchall()
            if rows:
                await conn.execute("UPDATE profiles SET platform=?, name=? WHERE id=?;",
                                   (platform, name, user_id,))
                await conn.commit()
            else:
                raise ProfileNotLinked()


async def select(user_id):
    """Select profiles if exists."""
    async with aiosqlite.connect("main.sqlite") as conn:
        async with conn.execute("SELECT platform, name FROM profiles WHERE id=?;", (user_id,)) as pool:
            rows = await pool.fetchall()
            if rows:
                return rows[0]
            raise ProfileNotLinked()


async def select_all(table):
    """Select everything from a table."""
    async with aiosqlite.connect("main.sqlite") as conn:
        async with conn.execute(f"SELECT * FROM {table}") as pool:
            rows = await pool.fetchall()
            if rows:
                return rows


async def remove_duplicates():
    """Remove duplicates in prefixes table."""
    async with aiosqlite.connect("main.sqlite") as conn:
        await conn.execute("DELETE FROM prefixes WHERE rowid NOT IN(SELECT min(rowid) FROM prefixes GROUP BY id);")
        await conn.commit()
