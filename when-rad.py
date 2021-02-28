import os
import subprocess
from tempfile import TemporaryFile

import param
import panel as pn
import numpy as np
import matplotlib.pyplot as plt
import holoviews as hv
from holoviews import opts

from templates.template import template
from static.css import css
from static.description import description
from static.blockquote import blockquote
from static.extras import extras
from static.returns import returns
from static.js import js

import config as c

hv.extension('bokeh', 'matplotlib')

pn.config.raw_css = [css,]

name = 'when-rad'
tmpl = pn.Template(template)
tmpl.add_variable('app_title', name)
tmpl.add_variable('description', description)
tmpl.add_variable('blockquote', blockquote)
tmpl.add_variable('extras', extras)
tmpl.add_variable('returns', returns)
tmpl.add_variable('js', js)

class Interact(param.Parameterized):
    '''

    '''
    def __init__(self, name):
        super(Interact, self).__init__()
        self.datapath = name + '/data'
        self.filelist = os.listdir(self.datapath)
        self.filelist.sort()
        self.cwd = name
        self.jitcache = f'{self.cwd}/_jitcache'
        self.jitscript = f'{self.cwd}/shadow.py'
        self.cachelist = os.listdir(self.jitcache)

    # TODO: improve default setting
    data = param.Selector(default='20190623_NNR300S20_correction.npz')
    time = param.Integer(0, bounds=(0,100))

    @staticmethod
    def _format_imshow(fig, ax, title, 
                        m=0.02, bgc='#292929', axc='#eee', lblc='#fff'):
        ax.margins(m)
        ax.set_aspect(aspect=1)
        ax.set_xlabel('Easting')
        ax.set_ylabel('Northing')
        ax.set_title(title, color=axc, loc='left', pad=20)
        ax.xaxis.label.set_color(lblc)
        ax.yaxis.label.set_color(lblc)
        ax.tick_params(axis='x', colors=lblc)
        ax.tick_params(axis='y', colors=lblc)
        ax.spines['bottom'].set_color(axc)
        ax.spines['top'].set_color(axc) 
        ax.spines['right'].set_color(axc)
        ax.spines['left'].set_color(axc)
        ax.set_facecolor(bgc)
        fig.patch.set_facecolor(bgc)

    @staticmethod
    def _format_polar(fig, ax, bgc='#292929', axc='#eee', lblc='#fff'):
        tks = [np.deg2rad(a) for a in np.linspace(0,360,8,endpoint=False)]
        xlbls = np.array(['N','45','E','135','S','225','W','315'])
        ax.set_theta_zero_location('N')
        ax.set_xticks((tks))
        ax.set_xticklabels(xlbls, rotation="vertical", size=12)
        ax.tick_params(axis='x', pad = 0.5)
        ax.set_theta_direction(-1)
        ax.set_rmin(0)
        ax.set_rmax(90)
        ax.set_rlabel_position(90)
        ax.set_facecolor(bgc)
        ax.spines['polar'].set_color(axc)
        ax.xaxis.label.set_color(lblc)
        ax.yaxis.label.set_color(lblc)
        ax.tick_params(axis='x', colors=axc)
        ax.tick_params(axis='y', colors=axc)
        fig.patch.set_facecolor(bgc)

    @staticmethod
    def _set_title(fn, opt='elevation'):
        '''Assigns titles for self._imshow().
        '''
        date = f'{fn[:4]}-{fn[4:6]}-{fn[6:8]}'

        if opt == 'elevation':
            addendum = ': Interpolation'
        elif opt == 'shadows':
            addendum = ': Shadows'

        return date + addendum

    def _imshow(self, array, opt, cmap='viridis'):
        '''Generalized method for calling plt.imshow()
        '''
        fig, ax = plt.subplots(1)
        ax.imshow(array, origin='lower', cmap=cmap,)
        title = self._set_title(fn=self.data, opt=opt)
        self._format_imshow(fig=fig, ax=ax, title=title)
        plt.close('all')
        return fig

    @staticmethod
    def _plot_overlay(elevation, shadows):
        '''

        '''
        shadows = hv.Dataset(
                    (
                    np.arange(shadows.shape[2]),
                    np.arange(shadows.shape[0]), 
                    np.arange(shadows.shape[1]), 
                    shadows
                    ),
                    ['Time', 'x', 'y'], 'Shadows')

        elevation = hv.Dataset(
                    (
                    np.arange(elevation.shape[0]),
                    np.arange(elevation.shape[1]), 
                    elevation),
                    ['x', 'y'], 'Elevation')
        
        opts.defaults(
            opts.Image('elevation', cmap='viridis', invert_yaxis=True),
            opts.Image('shadows', cmap='binary', invert_yaxis=True,
                        alpha=0.7),
            opts.Overlay(show_legend=False))

        elevation = elevation.to(hv.Image, ['x', 'y'], group='elevation')
        shadows = shadows.to(hv.Image, ['x', 'y'], group='shadows')

        return elevation * shadows
    
    def _update_filelist(self):
        '''
        '''
        self.param.data.default = self.filelist[0]
        self.param.data.objects = self.filelist

    def _check_existing_cache(self):
        '''
        '''
        self.dirname = self.data.replace('_correction.npz', '')
        if self.dirname in self.cachelist:
            self.cache_exists = True
        else:
            self.cache_exists = False


    @param.depends('data')
    def input(self):
        '''Assigns the self.filename and self.elevation
        instance variables. Returns as plot of self.elevation.
        '''
        self._update_filelist()
        self._check_existing_cache()
        self.cachepath = f'{self.jitcache}/{self.dirname}'

        if self.cache_exists == True:
            self.elevation = np.load(f'{self.cachepath}/elevation.npy')
            
        else:
            subprocess.run(['mkdir', self.cachepath])

            npz = np.load(f'{self.datapath}/{self.data}', allow_pickle=True)
            self.elevation = npz['elevation']
        
            np.save(f'{self.cachepath}/elevation.npy', self.elevation)
            np.save(f'{self.cachepath}/sunposition.npy', npz['sunposition'])

        self.param.time.bounds = (0, npz['sunposition'].shape[0])
        
        #return self._imshow(array=self.elevation, opt='elevation',)

    @param.depends('data', 'time')
    def output(self):
        '''
        '''

        if 'shadows.npy' in os.listdir(self.cachepath):
            pass
        else:
            subprocess.run(['python', self.jitscript, self.cachepath,])

        self.shadows = np.load(f'{self.cachepath}/shadows.npy')
    
        #return self._plot_overlay(self.elevation, self.shadows,)

        slice_ = self.shadows[:,:,self.time]
        return self._imshow(slice_, opt='shadows', cmap='binary')

    def export(self):
        '''
        '''
        outfile = TemporaryFile()
        np.savez(outfile,
                    shadows=self.shadows,
        )
        _ = outfile.seek(0)

        name = f'{self.data[:-4]}_correction.npz'
        return pn.widgets.FileDownload(file=outfile, filename=name)

    def plot_sun(self):
        '''Return a plot of sun position
        '''
        xs = np.deg2rad(self.correct.sunposition_df['azimuth'])
        ys = self.correct.sunposition_df['altitude']
        
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='polar')
        ax.scatter(xs,ys, s=10, c='orange',alpha=0.5)
        self._format_polar(fig=fig, ax=ax)
        plt.close('all')
        return fig


interact = Interact(name=name)

input_params = [interact.param.data, interact.param.time,]
output_params = []

tmpl.add_panel('A', pn.Column(interact.input, *input_params))
tmpl.add_panel('B', interact.output)
tmpl.add_panel('C', interact.export)
#tmpl.add_panel('D', interact.plot_sun)

tmpl.servable()
