from examples.activity.eg_01_activity_list import main as eg_01_activity_list
from examples.activity.eg_02_activity_get import main as eg_02_activity_get
from examples.activity.eg_03_activity_submit import main as eg_03_activity_submit
from examples.activity.eg_04_activity_report import main as eg_04_activity_report
from examples.activity.eg_06_activity_cancel import main as eg_06_activity_cancel

# run command: PYTHONPATH="$(pwd)/src:$(pwd)" python tests/examples/activity/run_all.py

try:
    eg_01_activity_list()
    eg_02_activity_get()
    eg_03_activity_submit()
    eg_04_activity_report()
    # eg_05_loss_export_submit()
    eg_06_activity_cancel()
    # Commented out as in 2.0 it won't be delivered to the customers
    # eg_07_activity_resubmit()

except Exception as e:
    print(f"Error running examples: {e}")
    exit(1)
