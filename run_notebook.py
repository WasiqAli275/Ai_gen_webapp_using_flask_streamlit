import nbformat
from nbclient import NotebookClient
p = r'c:\Users\zs\Desktop\streamlitwebapp\notebook\kaggle\competitions\hull_tactical_notebook.ipynb'
print('Reading', p)
nb = nbformat.read(p, as_version=4)
client = NotebookClient(nb, timeout=3600, kernel_name='python3')
print('Starting execution... this may take a while')
nb = client.execute()
nbformat.write(nb, p)
print('Execution finished')
