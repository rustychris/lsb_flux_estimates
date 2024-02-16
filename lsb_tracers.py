import stompy.model.delft.waq_scenario as dwaq
import six
import local_config
##

six.moves.reload_module(dwaq)
six.moves.reload_module(local_config)

hydro = dwaq.HydroFiles(hyd_path="../v148_jun_28_2016_dwaq_merge/com-v148_jun_28_2016_dwaq_merge.hyd")


class LsbTracers(local_config.LocalConfig, dwaq.WaqModel):
    integration_option="24.60"

    def setup_tracer_continuity(self):
        self.substances['continuity']=dwaq.Substance(initial=1.0)
        # This adds a concentration=1.0 boundary condition on all the boundaries.
        all_bcs=[b.decode() for b in np.unique(self.hydro.boundary_defs()['type'])]
        self.add_bc(all_bcs,'continuity',1.0)

    def setup_tracer_san_jose(self):
        self.substances['san_jose']=dwaq.Substance(initial=0)
        self.add_bc('SAN_JOSE_flow', 'san_jose',1.0)

    def setup_tracer_san_mateo(self):
        self.substances['san_mateo']=dwaq.Substance(initial=0)
        self.add_bc(['san_mateo'], 'san_mateo', 1.0)

    def setup_tracers(self):
        self.setup_tracer_continuity()
        self.setup_tracer_san_jose()
        self.setup_tracer_san_mateo()
        
    def run(self,force=False):
        assert self.base_path is not None,"Must specify base_path"
        
        if not force:
            if os.path.exists(os.path.join(self.base_path,'dwaq_map.nc')):
                log.info("Run seems to exist -- will not run again")
                return

        self.cmd_write_hydro()
        self.cmd_write_inp()
        self.cmd_delwaq1()
        self.cmd_delwaq2()
        self.cmd_write_nc()        


model = LsbTracers(hydro=hydro,base_path="/home/rusty/src/data_lsb_tracer",overwrite=True)

# Short run for testing
model.stop_time = model.start_time + np.timedelta64(1,'D')
model.setup_tracers()


model.run()
