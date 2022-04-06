import os

# The user home dir
home_dir = os.environ["HOME"]

# Where the CMR generates its various data files
work_dir = os.environ.get("WORK_DIR", os.path.join(home_dir,"work"))

# Where the clone of agave-model is stored
model_dir = os.environ.get("MODEL_DIR",None)
if model_dir is None:
    model_dir = os.path.join(home_dir, "agave-model")
    if os.path.exists(model_dir):
        pass
    elif os.path.exists("/agave-model"):
        model_dir = "/agave-model"

# Where the json config files are kept
json_dirs = [os.path.join(model_dir, "science-models", "JSONFiles"), os.path.join(work_dir, "machineFiles")]
os.makedirs(json_dirs[-1], exist_ok=True)

class in_dir:
    def __init__(self,dirname):
        self.save = None
        self.dirname = dirname
    def __enter__(self):
        self.save = os.getcwd()
        os.chdir(self.dirname)
    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.save)
