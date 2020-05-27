import pandas as pd
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import HTML
import dts_plot as dp


filename =  'C:/Users/OSL-ASUS-UX32V/Desktop/Test Data/CH02 0930_1030.csv'


class App:
    
    def __init__(self, df):
        self._df = df
       

        self._plot_container = widgets.Output()
        _app_container = widgets.VBox([
            self._plot_container,
        ], layout=widgets.Layout(align_items='center', flex='3 0 auto'))
        self.container = widgets.VBox([
            widgets.HBox([
                _app_container, 
            ])
        ], layout=widgets.Layout(flex='1 1 auto', margin='0 auto 0 auto', max_width='1024px'))
        self._update_app()
        
    @classmethod
    def from_url(cls, url):
        df = pd.read_csv(filename)
        return cls(df)
    
    
    def _create_plot(self,filename):
        canvas = dp.dts_plot(filename=filename)
        return canvas

    def _on_change(self, _):
        self._update_app()
        
    def _update_app(self):

        self._plot_container.clear_output(wait=True)
        with self._plot_container:
            canvas = self._create_plot(filename)
            canvas.show()
app = App.from_url(filename)

app.container
