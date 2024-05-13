from flask import Flask, Response
from flask_apscheduler import APScheduler
from k8sclient import K8SClient

import json


class Config:
    SCHEDULER_API_ENABLED = True


pods = {"CODE": 500, "BODY": None, "REASON": 'Backend is not ready'}

app = Flask(__name__)
app.config.from_object(Config())

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()


@scheduler.task('interval', id='job_get_pods', seconds=15)
def job_get_pods():
    global pods
    cluster = K8SClient()
    pods = cluster.get_all_pods()


@app.route("/api/v1/getPods", methods=['GET'])
def get_pods():
    global pods
    return Response(response=json.dumps(pods['BODY']).encode(),
                    status=pods['CODE'],
                    mimetype='application/json',
                    headers={"Access-Control-Allow-Origin": "*"})


if __name__ == '__main__':
    app.run()
