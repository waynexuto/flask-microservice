import concurrent
import threading
import warnings
import requests
import heapq
from concurrent.futures import ThreadPoolExecutor
from collections import OrderedDict
from flask import json, current_app
from urllib3.exceptions import InsecureRequestWarning
from model.employee import Employee, EmployeeEncoder
from model.denial import Denial
from model.executable import Executable
from model.intrusion import Intrusion
from model.misuse import Misuse
from model.other import Other
from model.probing import Probing
from model.unauthorized import Unauthorized

lock = threading.Lock()

def set_identities(mapping, cache):
    ''' set identities into cache '''
    if mapping or len(mapping.items()) > 0:
        cache.set("identity_by_ip", mapping)
        current_app.logger.info("identities snapshot saved in cache")
        return True
    return False

def get_identities(cache):
    ''' get identities from cache '''
    identities = cache.get("identity_by_ip")
    current_app.logger.info("get identities snapshot from cache")
    if identities:
        return identities

def set_incidents(incident_type,incident_results, cache):
    ''' set incidents snapshot into cache '''
    if incident_type and incident_results:
        results = incident_results['results']
        cache.set(incident_type, results)
        current_app.logger.info("Completed saving incidents snapshot: "+ incident_type + " to cache")
        return True
    return False

def get_incidents(incident_type, cache):
    ''' get incidents snapshot into cache '''
    incidents = cache.get(incident_type)
    current_app.logger.info("get incidents snapshot from cache")
    if incidents:
        return incidents

def get_employee_id_by_ip(internal_ip, cache):
    ''' get employee id base on identity ip address mapping'''
    if internal_ip in cache.get("identity_by_ip"):
        return cache.get("identity_by_ip")[internal_ip]

def sort_employees(heap):
    ''' heapsort employee objects base on employee id and return in ordered dict (hashmap)'''
    employees = OrderedDict()
    while len(heap) > 0:
        lock.acquire()
        employee = heapq.heappop(heap)
        employees[employee.id] = employee
        lock.release()
    return employees

def exist_in_heap(employee_id, heap):
    ''' check if employee object has already created base on give employee id '''
    for employee in heap:
        if employee_id == employee.id:
            return employee

def append_employee_group(employee_id, incident_obj, heap):
    ''' adding incident into employee's incident groups base on prioirty '''
    if employee_id not in heap:
        employee = Employee(employee_id)
    else:
        employee = exist_in_heap(employee_id, heap)
    employee.add_incident(incident_obj)
    return employee

def create_incident_from_json(incident_type, incident_json, cache):
    ''' deserialize json into incident objects '''
    employee_id = None
    incident_obj = None
    if incident_type == "denial":
        employee_id = incident_json["reported_by"]
        incident_obj = Denial.from_json(incident_json)
    elif incident_type == "misuse":
        employee_id = incident_json["employee_id"]
        incident_obj = Misuse.from_json(incident_json)
    elif incident_type == "unauthorized":
        employee_id = incident_json["employee_id"]
        incident_obj = Unauthorized.from_json(incident_json)
    elif incident_type == "intrusion":
        employee_id = get_employee_id_by_ip(incident_json["internal_ip"], cache)
        incident_obj = Intrusion.from_json(incident_json)
    elif incident_type == "executable":
        employee_id = get_employee_id_by_ip(incident_json["machine_ip"], cache)
        incident_obj = Executable.from_json(incident_json)
    elif incident_type == "probing":
        employee_id = get_employee_id_by_ip(incident_json["ip"], cache)
        incident_obj = Probing.from_json(incident_json)
    elif incident_type == "other":
        employee_id = get_employee_id_by_ip(incident_json["identifier"], cache)
        incident_obj = Other.from_json(incident_json)
    return employee_id, incident_obj

def group_incident_by_employee(incident_type, heap, cache):
    ''' group incidents by employee and incident type '''
    current_app.logger.info("start grouping incident_type: " + incident_type)
    incidents = cache.get(incident_type)
    if incidents and len(incidents) > 0:
        for incident_json in incidents:
            try:
                employee_id, incident_obj = create_incident_from_json(incident_type, incident_json, cache)
                if employee_id and incident_obj is not None:
                    employee = append_employee_group(employee_id, incident_obj, heap)
                    lock.acquire()
                    heapq.heappush(heap, employee)
                    lock.release()
            except Exception:
                current_app.logger.warn("can not find mapping employee id base on given ip address, dropping incident")
                current_app.logger.warn("incident JSON: " + str(incident_json))
                continue
        return incident_type

def group_all_incidents(executor, cache):
    '''group all incidents by employee id at the same time, reduce CPU-bound wait time by multithreading '''
    with current_app.test_request_context():
        heap = []
        incident_types = current_app.config['INCIDENTS_TYPES']
        future_to_group = {executor.submit(group_incident_by_employee, incident_type, heap, cache): incident_type for incident_type in incident_types}
        for future in concurrent.futures.as_completed(future_to_group):
            incident_type = future_to_group[future]
            try:
                result = future.result(timeout=current_app.config['THREAD_TIMEOUT'])
            except Exception as e:
                current_app.logger.error('group %r incident generated an exception: %s' % (incident_type, e))
            else:
                if result:
                    current_app.logger.info("Completed grouping incident snapshot: " + result)
        employees = sort_employees(heap)
        cache.set("employees", employees)
        current_app.logger.info("completed all incidents grouping")

def get_group_incidents_result(cache):
    ''' serialized cached group incidents result and return as JSON '''
    employees = cache.get("employees")
    if employees:
        return json.dumps(employees, cls=EmployeeEncoder, sort_keys=False)

def save_identities_snapshot(cache, timeout=300):
    ''' save identities raw data from upstream into cache '''
    current_app.logger.info("Saving identities snapshot to cache")
    url = current_app.config['BASE_ENDPOINT'] + "identities"
    warnings.simplefilter('ignore', InsecureRequestWarning)
    response = requests.get(url,  verify=False, timeout=timeout, auth=(current_app.config['SERVICE_ID'], current_app.config['SERVICE_PASSWORD']))
    if response.status_code == 200:
        return set_identities(json.loads(response.content), cache)
    current_app.logger.error("Upstream server API error, url: " + url)
    return False

def save_incident_snapshot(incident_type, cache, timeout=300):
    ''' save incidents raw data from upstream into cache '''
    current_app.logger.info("Saving incident snapshot: " + incident_type +" to cache")
    url = current_app.config['BASE_ENDPOINT'] + "incidents/" + incident_type
    warnings.simplefilter('ignore', InsecureRequestWarning)
    response = requests.get(url, verify=False, timeout=timeout, auth=(current_app.config['SERVICE_ID'], current_app.config['SERVICE_PASSWORD']))
    if response.status_code == 200:
        current_app.logger.debug("Returned JSON result for incident type: " + incident_type)
        current_app.logger.debug(json.loads(response.content))
        set_incidents(incident_type, json.loads(response.content), cache)
    return incident_type

def save_all_incidents_snapshot(executor, cache):
    '''save all incidents at the same time, reduce I/O-bound wait time by multithreading'''
    with current_app.test_request_context():
        incident_types = current_app.config['INCIDENTS_TYPES']
        future_to_snapshot = {executor.submit(save_incident_snapshot, incident_type, cache, current_app.config['THREAD_TIMEOUT']): incident_type for incident_type in incident_types}
        for future in concurrent.futures.as_completed(future_to_snapshot):
            incident_type = future_to_snapshot[future]
            try:
                result = future.result(timeout=current_app.config['THREAD_TIMEOUT'])
            except Exception as e:
                current_app.logger.error('save incident %r snapshot generated an exception: %s' % (incident_type, e))

def refresh_cache(executor, cache):
    ''' refresh cache periodically in background'''
    current_app.logger.info("start scheduled background task - cache refresh")
    save_identities_snapshot(cache)
    save_all_incidents_snapshot(executor, cache)
    group_all_incidents(executor, cache)
    current_app.logger.info("completed cache refresh")

