import uuid
import json

from flask import request, Response
from flask_restful import Resource
from database.db import initialize_db
from database.models import Task, Result, TaskHistory


class Tasks(Resource):
    def get(self):
        # Get all task objects and return them to the user
        tasks = Task.objects().to_json()
        return Response(tasks, mimetype="application/json", status=200)

    # Add Tasks
    def post(self):
        body = request.get_json()
        json_obj = json.loads(json.dumps(body))
        obj_num = len(body)
        # For each Task object, add it to the database
        for i in range(len(body)):
            json_obj[i]['task_id'] = str(uuid.uuid4())
            Task(**json_obj[i]).save()
            task_options = []
            for key in json_obj[i].keys():
                if (key != "task_type" and key != "task_id"):
                    task_options.append(key + ": " + json_obj[i][key])
                    
            # Add to task history
            TaskHistory(
                task_id=json_obj[i]['task_id'],
                task_typt=json_obj[i]['task_type'],
                task_object=json.dumps(json_obj),
                task_options=task_options,
                task_result=""
            ).save()
            
        return Response(Task.objects.skip(Task.objects.count() - obj_num).to_json(), mimetype="application/json", status=200)


class Results(Resource):
    def get(self):
        results = Result.objects().to_json()
        return Response(results, mimetype="application/json", status=200)

    def post(self):
        # Check if results from the implant are populated
        if str(request.get_json()) != '{}':
            body = request.get_json()
            print("Received implant response: {}".format(body))
            json_obj = json.loads(json.dumps(body))
            json_obj['result_id'] = str(uuid.uuid4())
            Result(**json_obj).save()
            
            # Clear tasks so they don't execute twice
            tasks = Task.objects().to_json()
            Task.objects().delete()
            return Response(tasks, mimetype="application/json", status=200)
        
        else:
            tasks = Task.objects().to_json()
            Task.objects().delete()
            return Response(tasks, mimetype="application/json", status=200)


class History(Resource):
    def get(self):
        task_history = TaskHistory.objects().to_json()
        results = Result.objects().to_json()
        json_obj = json.loads(results)
        
        # Format each result from the implant to be more friendly for consumption/display
        result_obj_collection = []
        for i in range(len(json_obj)):
            for field in json_obj[i]:
                result_obj = {
                    "task_id": field,
                    "task_results": json_obj[i][field]
                }
                result_obj_collection.append(result_obj)
                
        # For each result in the collection, check for a corresponding task ID and if there's a match, update it with the results.
        for result in result_obj_collection:
            if TaskHistory.objects(task_id=result["task_id"]):
                TaskHistory.objects(task_id=result["task_id"]).update_one(
                    set__task_results=result["task_results"])
        return Response(task_history, mimetype="application/json", status=200)
