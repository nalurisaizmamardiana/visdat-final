#!/usr/bin/env python
# coding: utf-8

# In[11]:


import pandas as pd
import numpy as np

from bokeh.plotting import figure
from bokeh.io import show, output_notebook, push_notebook, curdoc

from bokeh.models import Quad, ColumnDataSource, HoverTool, CategoricalColorMapper, Panel, CustomJS, Dropdown, Select
from bokeh.models.widgets import CheckboxGroup, Slider, RangeSlider, Tabs

from bokeh.layouts import column, row, WidgetBox
from bokeh.palettes import Category20_16, Spectral4

from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application


# In[12]:


from bokeh.io import output_notebook, show

from bokeh.plotting import figure 

from bokeh.models import CustomJS, ColumnDataSource, Panel, Tabs, DatetimeTickFormatter, HoverTool, NumeralTickFormatter
from bokeh.models.widgets import Select, DateRangeSlider

from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler

from bokeh.layouts import column, row


# In[13]:


data = pd.read_csv("Indonesia_coronavirus_daily_data.csv")


# In[14]:


data


# In[15]:


prov = list(data.Province.unique())

DataList = list(data.columns)


# In[16]:


def newData(dt, feature):

    
    xs = []
    ys = []
    colors = []
    labels = []

    for i, prov in enumerate(dt):

        dat = data[data['Province'] == prov].reset_index(drop = True)
        
        x = list(dat['Daily_Case'])
        y = list(dat[feature])
        
        xs.append(list(x))
        ys.append(list(y))

        colors.append(Category20_16[i])
        labels.append(prov)

    new_src = ColumnDataSource(data={'x': xs, 'y': ys, 'color': colors, 'label': labels})

    return new_src


# In[17]:


#Functiuon to make the plot from the data obtained/updated at each selection in the ColumnDataSource
def plotGraf(src, feature):
    
    plot = figure(plot_width = 700, plot_height = 400, 
            title = 'Death by Cumulative Case',
            x_axis_label = 'Kasus Kumulative', y_axis_label = 'Jumlah Kematian')

    plot.multi_line('x', 'y', color = 'color', legend_field = 'label', line_width = 2, source = src)

    return plot


# In[18]:


def provinceUpdate(prv, dtLama, dtBaru):
    
    plot = [chbx.labels[i] for i in chbx.active]   
    new_src = newData(plot, fitur.value)
    src.data.update(new_src.data)


# In[19]:


def fiturUpdate(ftr, dtLama, dtBaru):
    
    plot = [chbx.labels[i] for i in chbx.active]    
    feature = fitur.value   
    new_src = newData(plot, feature)
    src.data.update(new_src.data)


# In[20]:



chbx = CheckboxGroup(labels=prov, active = [0])
chbx.on_change('active', provinceUpdate)


#Drop down 
fitur = Select(options = DataList[2:], value = 'Daily_Case', title = 'Pilih Fitur')
fitur.on_change('value', fiturUpdate)

#Default province
province = [chbx.labels[i] for i in chbx.active]

#Make default ColumnDataSource instance
src = newData(province, fitur.value)

#Plot  data
p = plotGraf(src, fitur.value)

# Put controls in a single element
controls = WidgetBox(fitur, chbx)

# Create a row layout
layout = row(controls, p)


# In[21]:


def tab_barplot(data):
    
    source = ColumnDataSource(data)
    p = figure(y_range=data['Province'], 
               title="Jumlah Kasus Tiap Provinsi",
               plot_height=800,
               plot_width=800,
               toolbar_location=None)

    p.hbar(y='Province', right='Cumulative_Case', source=source, height=1)

    p.x_range.start = 0
    p.xaxis.formatter = NumeralTickFormatter(format="0")
    
    return Panel(child=p, title="BAR PLOT")


# In[22]:


df_province = data.groupby(['Province']).sum()
df_province = df_province.reset_index()


# In[23]:


df_daily_total = data.groupby(['Date']).sum()
df_daily_total = df_daily_total.reset_index()


# In[24]:


def tab_lineplot(data):
    
    source = ColumnDataSource(data)
    
    hover = HoverTool(
        tooltips=[('Timestamp', '@x{%Y-%m-%d}'), ('Value', '@y')],
        formatters={'x': 'datetime'},)

    date_range_slider = DateRangeSlider(title="Rentang Tanggal", 
                                        start=data['Date'].min(), 
                                        end=data['Date'].max(),
                                        value=(data['Date'].min(), data['Date'].max()), 
                                        step=1, 
                                        width=300)

    p = figure(x_range=df_daily_total['Date'],
               x_axis_type='datetime',
               x_axis_label='Date',
               y_axis_label='Jumlah Kasus',
               plot_height=500,
               plot_width=750,
               title='Jumlah Kasus COVID-19')
    
    p.line('Date', 'Cumulative_Case', source=source)
    p.add_tools(hover)
    p.xaxis.formatter = DatetimeTickFormatter(days = ['%F']) 
    
    callback = CustomJS(args=dict(source=source, ref_source=source), code="""   
        console.log(cb_obj.value); 
        const date_from = Date.parse(new Date(cb_obj.value[0]).toDateString());
        const date_to = Date.parse(new Date(cb_obj.value[1]).toDateString());

        const data = source.data;
        const ref = ref_source.data;

        const from_pos = ref["x"].indexOf(date_from);
        const to_pos = ref["x"].indexOf(date_to);

        data["y"] = ref["y"].slice(from_pos, to_pos);
        data["x"] = ref["x"].slice(from_pos, to_pos);

        source.change.emit();
    """)
    
    date_range_slider.js_on_change('value', callback)
    
    layout = column(date_range_slider, p)
    
    lineplot = Panel(child=layout, title="LINE PLOT")
    
    return lineplot


# In[25]:


bar = tab_barplot(df_province)
line = tab_lineplot(df_daily_total)
first_panel = Panel(child=layout, title='Death by Cumulative Case ')
tabs = Tabs(tabs=[line,first_panel,bar])


# In[26]:


show(tabs)


# In[27]:


curdoc().add_root(tabs)


# In[ ]:




