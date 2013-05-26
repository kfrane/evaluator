import lxc
import subprocess

class MyContainer(lxc.Container):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  def attach(self, namespace="ALL", *cmd):
    """
            Attach to a running container.
            Copied from the lxc source code.
            It returns return code of the executed process,
            as oppose to orignal version that returns bool.
    """

    if not self.running:
      return False

    attach = ["lxc-attach", "-n", self.name,
        "-P", self.get_config_path()]
    if namespace != "ALL":
      attach += ["-s", namespace]

    if cmd:
      attach += ["--"] + list(cmd)

    return subprocess.call(
        attach,
        universal_newlines=True)

