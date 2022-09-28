import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import datetime
import cmocean
import os
import sys

#date range
t1 = datetime.datetime(2021, 1, 1, 0, 0, 0)
dt = datetime.timedelta(hours=6)
nt = 41
nens = 10
x, y = np.load('output/grid.npy')
ny, nx = x.shape
plot_crs = ccrs.NorthPolarStereo(central_longitude=-45, true_scale_latitude=60)

v=int(sys.argv[1])  ##variable type
s=int(sys.argv[2])  ##scale, -1 if full scale

vname = ('sic', 'sit', 'velocity', 'damage', 'deform')[v]
vmin = (     0,     0,          0,      0.8,        0)[v]
vmax = (     1,     3,        0.3,        1,      0.3)[v]
dv = (vmax-vmin)/40

if s==-1:
    sstr = ''
else:
    sstr = '_scale{}'.format(s+1)

if not os.path.exists('output/figs/'+vname+sstr+'/sprd'):
    os.makedirs('output/figs/'+vname+sstr+'/sprd')

for n in range(nt):
    t = t1 + n*dt
    tstr = t.strftime('%Y%m%dT%H%M%SZ')

    var_mean = np.zeros((ny, nx))
    var_sprd = np.zeros((ny, nx))
    if vname=='velocity':
        u_mean = np.zeros((ny, nx))
        v_mean = np.zeros((ny, nx))
        for m in range(nens):
            u_mean += np.load('output/ensemble_run/{:03d}'.format(m+1)+'/siu'+sstr+'_'+tstr+'.npy')
            v_mean += np.load('output/ensemble_run/{:03d}'.format(m+1)+'/siv'+sstr+'_'+tstr+'.npy')
        u_mean = u_mean/nens
        v_mean = v_mean/nens
        for m in range(nens):
            var_sprd += (np.load('output/ensemble_run/{:03d}'.format(m+1)+'/siu'+sstr+'_'+tstr+'.npy') - u_mean)**2
            var_sprd += (np.load('output/ensemble_run/{:03d}'.format(m+1)+'/siv'+sstr+'_'+tstr+'.npy') - v_mean)**2
        var_sprd = np.sqrt(var_sprd/(nens-1))

    else:
        for m in range(nens):
            var_mean += np.load('output/ensemble_run/{:03d}'.format(m+1)+'/'+vname+sstr+'_'+tstr+'.npy')
        var_mean = var_mean/nens
        for m in range(nens):
            var_sprd += (np.load('output/ensemble_run/{:03d}'.format(m+1)+'/'+vname+sstr+'_'+tstr+'.npy') - var_mean)**2
        var_sprd = np.sqrt(var_sprd/(nens-1))

    fig, ax = plt.subplots(1, 1, figsize=(10, 8), subplot_kw={'projection': plot_crs})
    var_sprd[np.where(var_sprd>10*dv)] = 10*dv
    c = ax.contourf(x, y, var_sprd, np.arange(0, 11*dv, dv), cmap='Reds')
    plt.colorbar(c, fraction=0.025, pad=0.015)
    ax.add_feature(cfeature.LAND, facecolor='gray', edgecolor='black', zorder=10, alpha=0.5)
    ax.set_title(vname+' ensemble spread '+t.strftime('%Y-%m-%d %H:%M'), fontsize=20)
    ax.set_xlim(-2.2e6, 1.3e6)
    ax.set_ylim(-1.1e6, 2e6)
    plt.savefig('output/figs/'+vname+sstr+'/sprd/{:03d}.png'.format(n), dpi=200)
    plt.close()
