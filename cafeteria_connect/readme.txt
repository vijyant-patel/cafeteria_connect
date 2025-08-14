docker exec -itu root django_01 bash
source venv_django_01/bin/activate
cd cafeteria_connect/backend/

python core/kafka/consumer.py
celery -A config worker --loglevel=info
daphne -p 8002 config.asgi:application



python manage.py shell
import redis, json
r = redis.StrictRedis(host='cafeteria_connect-redis-1', port=6379, db=0)
r.publish('order_updates', json.dumps({'message': '🔥 Test message'}))

supervisor:-
docker exec -it django_01 bash
apt-get update && apt-get install -y supervisor
mkdir -p /var/log/supervisor

/etc/supervisor/conf.d/django_services.conf

create /var/log/supervisor/
supervisord -c /etc/supervisor/supervisord.conf
supervisorctl reread
supervisorctl update
supervisorctl status
supervisorctl stop all
supervisorctl start all
supervisorctl start celery_worker
supervisorctl stop celery_worker