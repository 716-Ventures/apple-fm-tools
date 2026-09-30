import unittest
from unittest.mock import patch
from apple_fm_tools import worker

class WorkerTests(unittest.TestCase):
 def test_unknown_job_rejected(self):
  with self.assertRaises(worker.WorkerError):worker.run_job({'job':'approval','state':'x'})
 def test_large_input_escalates_before_generation(self):
  with patch.object(worker,'command',side_effect=['{}','3000']) as cmd:
   with self.assertRaises(worker.WorkerError):worker.run_job({'job':'summary','state':'long'})
  self.assertEqual(cmd.call_count,2)
 def test_bad_label_rejected(self):
  with patch.object(worker,'command',side_effect=['{}','10','{"value":"invented"}']):
   with self.assertRaises(worker.WorkerError):worker.run_job({'job':'route','state':'task'})
 def test_publish_checks_ownership_and_document(self):
  task={'id':'issue','title':'title','assigneeAgentId':'agent','status':'todo'}
  calls=[]
  def api(method,path,body=None):
   calls.append((method,path,body))
   if path.endswith('/documents/apple-local-summary'):
    if method=='PUT':return {'latestRevisionId':'rev'}
    return {'body':'Apple local summary suggestion (requires agent review):\n\nSummary'}
   if path.endswith('/documents'):return []
   return task
  with patch.dict('os.environ',{'PAPERCLIP_TASK_ID':'issue','PAPERCLIP_AGENT_ID':'agent'}),patch.object(worker,'api',side_effect=api),patch.object(worker,'run_job',return_value={'value':'Summary'}):
   r=worker.paperclip('summary',True)
  self.assertEqual(r['document_revision'],'rev')
  self.assertTrue(any(path.endswith('/checkout') for _,path,_ in calls))
  self.assertFalse(any(method=='PATCH' for method,_,_ in calls))
 def test_foreign_task_is_rejected(self):
  with patch.dict('os.environ',{'PAPERCLIP_TASK_ID':'issue','PAPERCLIP_AGENT_ID':'agent'}),patch.object(worker,'api',return_value={'assigneeAgentId':'other'}):
   with self.assertRaises(worker.WorkerError):worker.paperclip('summary',True)
class ValidationTests(unittest.TestCase):
 def test_nonobject_request_rejected(self):
  with self.assertRaises(worker.WorkerError):worker.run_job([])
 def test_fractional_severity_rejected(self):
  with patch.object(worker,'command',side_effect=['{}','10','{"value":1.5}']):
   with self.assertRaises(worker.WorkerError):worker.run_job({'job':'severity','state':'task'})
 def test_long_summary_rejected(self):
  import json
  with patch.object(worker,'command',side_effect=['{}','10',json.dumps({'value':'word '*71})]):
   with self.assertRaises(worker.WorkerError):worker.run_job({'job':'summary','state':'task'})

if __name__=='__main__':unittest.main()
