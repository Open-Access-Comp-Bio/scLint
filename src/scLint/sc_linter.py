from scLint.linter import check_integrity, check_obs, check_vars, print_report, save_plot
import scanpy as sc

""""
Potential wireframe for scLinter class. Ask Steve if it's worth it
Why I think it's useful, easier to read through the code.
"""

# TODO inquire if exploration should be in scLint --> Fundamentally what is a linter for?
# TODO inquire if checking vars and obs is necessary --> Does this answer the above?
# TODO inquire do we need an scExplore class? --> Or is scLinter and scExplorer the same? --> Not needed scLinter should do standard QC

class scLinter:
    def __init__(self,inspect_cols:list,adata_file=None,adata_var=None):
        # TODO add datatype assertions where applicable
        # TODO additional variables are probably needed
        self.adata = adata_var
        self.adata_file = adata_file
        # NOTE list of columns to do the linting with
        self.inspect = inspect_cols
        self.adata_var = adata_var
        self.integrity_status = None
        self.obs_status = None
        self.vars_status = None
    
    def open_adata(self):
        self.adata = sc.read_h5ad(self.adata_file)

    def run_integrity_check(self,logger):
        self.integrity_status = check_integrity(self.adata, logger)

    def run_obs_check(self,logger):
        self.obs_status = check_obs(self.adata, logger)
    
    def run_vars_check(self,logger):
        self.vars_status = check_vars(self.adata, logger)

    def linter_results(self):
        results = {'integrity':self.integrity_status,
                   'obs':self.obs_status,
                   'var':self.vars_status,
                   }
        return results

