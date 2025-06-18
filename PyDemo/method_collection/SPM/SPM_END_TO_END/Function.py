from comm.script.writeLogs import logger
from PyDemo.method_collection import request_in_a_function
from comm.unit.GlobalVariable import GlobalData


def func_wait_until_report_submission_completed(**kwargs):
    # dicts are lists of information set as global variables
    # {"name": "Variable name", "jsonpath": "jsonpath expression"}
    # tips: 1.You can also set global variables before executing the current function if necessary
    #         setattr(GlobalData.local_data.namespace, "variable name", "variable value")
    #       2.You can also modify the input keyword parameters(kwargs)
    #         and then pass the parameters into request_in_a_function

    dicts = [{"name": "GD_userName", "jsonpath": "$..userName"},
             {"name": "GD_userId", "jsonpath": "$..userId"}]
    request_in_a_function(r"/SPM/SPM_END_TO_END/end_to_end_resource.yaml", "get report submission status",
                          "get report submission status until pass", new_path= f"/itg/rest2/reports/{reportReferenceCode}/reportSubmission/{reportSubmissionId}",dicts, **kwargs)
