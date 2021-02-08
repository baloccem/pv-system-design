#!/usr/bin/env python

import pandas as pd
import numpy as np

'''
Module to calculate a PV solar system for householder
It consist in:
- Cell modules
- Inverter 

-----Work in progress-----

Author : Emilio Balocchi

'''

shading_losses = pd.read_csv('shading_losses.txt',sep=r'\s+', header = 0, skiprows = 0 )
shading_losses = shading_losses.set_index(['Month'])


class Radiation():
    '''
    Calculation of real total radiation for the spefific location
    Fill data in shading_losses.txt
    using data from https://pvwatts.nrel.gov/index.php
    '''
    
    def __init__(self,azimuth,tilt,location,lowest_T,hottest_Month,type_inst,df_shl):
        self.azimuth = azimuth
        self.tilt = tilt
        self.location = location
        self.lowest_T = lowest_T
        self.hottest_Month = hottest_Month
        self.type_inst = type_inst
        self.df_shl = df_shl

    def total_annual_energy(self,TAE):
        return TAE

    def total_full_sun_hours_year(self,ASR):
        return 365*ASR
    
    def shading_losses(self):
        self.df_shl['Monthly solar radiation [kW/m2]'] = \
            self.df_shl['Days']*self.df_shl['Daily solar Radiation']
        self.df_shl['Solar loss [kWh/m2]'] = \
            self.df_shl['Monthly solar radiation [kW/m2]']* \
                self.df_shl['Shading %']/100
        return self.df_shl
    
    def shading_losses_total(self):
        return  self.df_shl['Solar loss [kWh/m2]'].sum()
    
    def annual_solar_radiation(self):
        return  self.df_shl['Monthly solar radiation [kW/m2]'].sum()

    def shading_annual_percentage_loss(self):
        return self.shading_losses_total()/ \
            self.annual_solar_radiation()
    def real_solar_radiation(self):
        return self.annual_solar_radiation() - \
            self.shading_losses_total()



class CellModule():
    '''
    Calculate number of cell modules to conform the cell module array
    '''
    def __init__(self,target,Voc,Isc,Vmp,Imp,P_nom,T_coef_V_C=0,T_coef_perc=0):
        self.target = target
        self.Voc = Voc
        self.Isc = Isc
        self.Vmp = Vmp
        self.Imp = Imp
        self.P_nom = P_nom
        self.T_coef_V_C = T_coef_V_C
        self.T_coef_perc = T_coef_perc

    def num_of_modules(self):
        return np.ceil(self.target / self.P_nom)  # rounding up

    def power_nameplate_rating(self):
        return self.num_of_modules()*self.P_nom

class Inverter():
    pass

pv = Radiation(170,33.69,'San Diego',-4,38,'Roof mounted',shading_losses)


pv.total_annual_energy(8105)
pv.total_full_sun_hours_year(5.72)
print(pv.shading_losses())
print('**************************************************************')
print('shading_losses_total = ',pv.shading_losses_total(),' h/y')
print('annual_solar_radiation = ', pv.annual_solar_radiation(),'kWh/m2/y')
print('shading_annual_percentage_loss = ',pv.shading_annual_percentage_loss(),' %')
print('real_solar_radiation = ',pv.real_solar_radiation(),' kWh/m2/y')


module = CellModule(5200,64.9,6.46,54.7,5.98,327,-0.176,0)
print('num_of_modules (rounding up) = ',module.num_of_modules())
print('power_nameplate_rating = ',module.power_nameplate_rating(),' W')
print('**************************************************************')
    
