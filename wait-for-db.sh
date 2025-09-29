
echo "Esperando o Postgres..."
while ! pg_isready -h db -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do
  sleep 2
done

echo "Postgres pronto! Iniciando API..."
exec "$@"
