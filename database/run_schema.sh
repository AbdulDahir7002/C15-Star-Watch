source .env
export PGPASSWORD=$DB_PASSWORD
psql -h $DB_HOST -d postgres -U $DB_USERNAME -d $DB_NAME -p $DB_PORT -f alter.sql