from Base import ControllerBase
from chaco.api import ArrayPlotData, BasePlotContainer, Plot

from traits.api import Instance, on_trait_change
import numpy as np

from save_plot import SaveFileController

import enaml
with enaml.imports():
    from analyzarr.ui.save_plot import SavePlotDialog
from enaml.application import Application
from enaml.stdlib.sessions import simple_session

class BaseImageController(ControllerBase):
    plot = Instance(BasePlotContainer)
    plotdata = Instance(ArrayPlotData)
    
    def __init__(self, parent, treasure_chest=None, data_path='/rawdata', *args, **kw):
        super(BaseImageController, self).__init__(parent, treasure_chest, data_path,
                                              *args, **kw)
        self.plotdata = ArrayPlotData()
        self._can_save = True
        self._can_change_idx = True

    def init_plot(self):
        self.plotdata.set_data('imagedata', self.get_active_image())
        self.plot = self.get_simple_image_plot(array_plot_data = self.plotdata,
                title = self.get_active_name()
                )

    def data_updated(self):
        # reinitialize data
        self.__init__(parent = self.parent, treasure_chest=self.chest,
                      data_path=self.data_path)

    # this is a 2D image for plotting purposes
    def get_active_image(self):
        nodes = self.chest.list_nodes('/rawdata')
        if len(nodes) > 0:
            return nodes[self.selected_index][:]

    def get_active_name(self):
        nodes = self.chest.list_nodes('/rawdata')
        return nodes[self.selected_index].name
    
    @on_trait_change("selected_index")
    def update_image(self):
        if self.chest is None or self.numfiles<1:
            return
        # get the old image for the sake of comparing image sizes
        old_data = self.plotdata.get_data('imagedata')
        active_image = self.get_active_image()
        self.plotdata.set_data("imagedata", active_image)
        self.set_plot_title(self.get_active_name())
        if old_data.shape != active_image.shape:
            grid_data_source = self._base_plot.range2d.sources[0]
            grid_data_source.set_data(np.arange(active_image.shape[1]), 
                                  np.arange(active_image.shape[0]))
            self.plot = self.get_simple_image_plot(array_plot_data = self.plotdata,
                    title = self.get_active_name())
            self.plot.aspect_ratio=(float(active_image.shape[1])/active_image.shape[0])

    def open_save_UI(self, plot_id='plot'):
        save_controller = SaveFileController(plot=self.get_plot(plot_id), parent=self)
        save_dialog = simple_session('save', 'Save dialog', SavePlotDialog, 
                                      controller=save_controller)
        Application.instance().add_factories([save_dialog])
        session_id = Application.instance().start_session('save')
        save_controller._session_id = session_id
