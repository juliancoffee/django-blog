# this is probably not viable for production, but at least it worked in docker
#
# I'm not exactly sure how it should be done in real environment, I'd guess it
# should be automated somehow with backups periodically going to s3 or smth
#
# and then rolled back from there, if needed
#
# but yeah, for me the process is simpler
#
# I assume that our user is postgres, db is called the same and you don't need
# any passwords or such

# this script isn't supposed to be run as is
echo "don't run it, read it"
exit 1

# 1. dump the backup
pg_dump -U postgres > dump.sql

# 2. do your thing which may break things
# ...
# ...

# 3. if it did, recreate db and restore its contents from the backup file
dropdb -U postgres postgres
createdb -U postgres postgres
psql -U postgres --single-transaction < dump.sql

# I guess I might come up with some automated way to do it using docker utils,
# but for now, it is better than nothing.
