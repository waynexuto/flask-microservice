from flask_apscheduler import APScheduler
from flask_caching import Cache
from flask_executor import Executor
from flask_httpauth import HTTPBasicAuth
from flask import request
from app import factory, service

# initialize
app = factory.create_app()
cache = Cache()
cache.init_app(app)
executor = Executor(app)
auth = HTTPBasicAuth()
limiter = factory.make_limiter(app)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# rest endpoints
@app.route('/')
@app.route('/server_status')
@auth.login_required
def index():
    '''index page'''
    app.logger.info("API endpoint /server_status is called")
    return "Server is alive!"

@app.route('/incidents', methods=['GET'])
@limiter.limit(app.config['INCIDENTS_API_RATE_LIMITS'])
@auth.login_required
def get_incidents():
    ''' get incidents group by employee id, if data in cache fetch from cache
    else call refresh_cache to process data calculation and return'''
    response_status = 200
    if not cache.get("employees"):
        service.refresh_cache(executor, cache)
    response_json = service.get_group_incidents_result(cache)
    if not response_json or len(response_json) == 0:
        response_json = {}
        response_status = 401
    response = app.response_class(response=response_json,status=response_status,mimetype='application/json')
    return response

@app.route('/shutdown', methods=['GET'])
@auth.login_required
def shutdown():
    ''' gracefully shutdown scheduler and server'''
    scheduler.shutdown(wait=True)
    shutdown_server = request.environ.get('werkzeug.server.shutdown')
    shutdown_server()
    response = app.response_class(response='shutting down server...',status=200,mimetype='text/html')
    return response

@scheduler.task('interval', id='background_refresh_cache', seconds=app.config['DEFAULT_CACHE_REFRESH'])
def background_refresh_cache():
    ''' refresh cache by time interval'''
    with app.app_context():
        service.refresh_cache(executor, cache)

@auth.verify_password
def authen(username, password):
    ''' this authen logic is subject to change, password hash and secrete key should be introduced'''
    if username == app.config['SERVICE_ID'] and password == app.config['SERVICE_PASSWORD']:
        app.logger.info("User: " + username + " logged in")
        return True
    return False

if __name__ == "__main__":
    app.run(host=app.config['SERVER_HOST'], debug=app.config['DEBUG'], port=app.config['SERVER_PORT'])


