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


class Radiation:
    '''
    Calculation of real total radiation for the spefific location
    Fill data in shading_losses.txt
    using data from https://pvwatts.nrel.gov/index.php
    '''
    
    def __init__(self,azimuth,tilt,location,type_inst,df_shl):
        self.azimuth = azimuth
        self.tilt = tilt
        self.location = location
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

    def __str__(self):
        return '''
        {}

        ------------------------------------------------------------------------- 
        Radiation and Shading losses
        -------------------------------------------------------------------------
        Shading losses total = Sum of Solar Loss              = {:7.2f} kWh/m2/y
        Annual solar radiation = Sum of Monthly solar Rad.    = {:7.2f} kWh/m2/y
        Shading annual percentage loss = {:7.2f} / {:7.2f}    = {:7.2f} %
        Real solar radiation =  {:7.2f} - {:7.2f}             = {:7.2f} kWh/m2/y
        '''.format(self.df_shl, self.shading_losses_total(),self.annual_solar_radiation(), \
        self.shading_losses_total(), self.annual_solar_radiation(), \
        self.shading_annual_percentage_loss()*100, self.annual_solar_radiation(),  \
        self.shading_losses_total(), self.real_solar_radiation())


class CellModule:
    '''
    Calculate number of cell modules to conform the cell module array
    roof = 1: roof mount;  0: open rack
    '''
    def __init__(self,target,Voc,Isc,Vmp,Imp,P_nom,lowest_T, \
        T_hottest_month,T_coef_V_C=0,T_coef_perc=0, T_amb = 25,roof=1):
        self.target = target
        self.Voc = Voc
        self.Isc = Isc
        self.Vmp = Vmp
        self.Imp = Imp
        self.P_nom = P_nom
        self.T_coef_V_C = T_coef_V_C
        self.T_coef_perc = T_coef_perc
        self.lowest_T = lowest_T
        self.T_hottest_month = T_hottest_month
        self.T_amb = T_amb
        self.roof = roof

    def num_of_modules(self):
        return np.ceil(self.target / self.P_nom)  # rounding up

    def power_nameplate_rating(self):
        return self.num_of_modules()*self.P_nom

    def Voltage_deviation(self, input):
        '''
        calculation of Voc adjusted
        '''
        if input == 'cold':
            T_deviation = self.ColdTempDeviation()
        else:
            T_deviation = self.WarmTempDeviation()
        if self.T_coef_V_C != 0 and self.T_coef_perc == 0:
            self.V_deviation = (T_deviation * self.T_coef_V_C)
        elif self.T_coef_V_C == 0 and self.T_coef_perc != 0:
            self.V_deviation_perc = (self.T_coef_perc*T_deviation)
            self.V_deviation = self.V_deviation_perc*self.Voc
        return self.V_deviation
    
    def ColdTempDeviation(self):
        return self.T_amb - self.lowest_T
    
    def Voc_adjusted(self):
        return self.Voc - self.Voltage_deviation('cold')

    def WarmTempereture(self):
        if self.roof == 1:
            return self.T_hottest_month + 30
        else:
            return self.T_hottest_month
    
    def WarmTempDeviation(self):
        return self.T_amb - self.WarmTempereture() 

    def Vmp_adjusted(self):
        return self.Vmp - self.Voltage_deviation('warm')
    
    def array_type(self):
        if self.roof == 1:
            return 'Roof Mounth -> Warm Temperature = 30°C + Hottest month average'
        elif self.roof == 2:
            return 'Open Rack' 

    def __str__(self):
        return '''
        -------------------------------------------------------------------------
        Target
        ------------------------------------------------------------------------- 
        Target power capacity                                   = {:7.2f} W
        Nominal power selected module                           = {:7.2f} W
        Num of modules (rounding up) = {:7.0f} / {:7.0f}        = {:7.0f} 
        Power nameplate rating                                  = {:7.2f} W 

        -------------------------------------------------------------------------
        Module
        -------------------------------------------------------------------------
        Voc                                                     = {:7.2f} V
        Isc                                                     = {:7.2f} A
        Vmp                                                     = {:7.2f} V
        Imp                                                     = {:7.2f} A
        Temperature Coefficient of VOC                          = {:7.3f} V/°C

        -------------------------------------------------------------------------
        Voc
        -------------------------------------------------------------------------
        Coldest day record                                      = {:7.2f} °C
        T ambient                                               = {:7.2f} °C
        Temperature deviation = Tamb - Coldest record           = {:7.2f} K
        Voltage deviation  =   {:7.3f} * {:7.2f}                = {:7.2f} V
        Voc adjusted =   {:7.2f} + {:7.2f}                      = {:7.2f} V

        -------------------------------------------------------------------------
        Vmp
        -------------------------------------------------------------------------
        Warmest average month                                   = {:7.2f} °C
        {}
        Warm temperature                                        = {:7.2f} °C
        Temperature deviation = Tamb - Warmest Avg. month       = {:7.2f} °C
        Voltage deviation =   {:7.3f} * {:7.2f}                 = {:7.2f} V
        Vmp adjusted                                            = {:7.2f} V

        '''.format(                           \
            self.target,                      \
            self.P_nom,                       \
            self.target,                      \
            self.P_nom,                       \
            self.num_of_modules(),            \
            self.power_nameplate_rating(),    \
            self.Voc,                         \
            self.Isc,                         \
            self.Vmp,                         \
            self.Imp,                         \
            self.T_coef_V_C,                         \
            self.lowest_T,                    \
            self.T_amb,                       \
            self.ColdTempDeviation(),          \
            self.T_coef_V_C,                  \
            self.ColdTempDeviation(),          \
            self.Voltage_deviation('cold'),      \
            self.Voc,                         \
            self.Voltage_deviation('cold'),     \
            self.Voc_adjusted(),              \
            self.T_hottest_month,              \
            self.array_type(),              \
            self.WarmTempereture(),              \
            self.WarmTempDeviation(),              \
            self.T_coef_V_C,              \
            self.WarmTempDeviation(),              \
            self.Voltage_deviation('warm'),        \
            self.Vmp_adjusted(),        \


        )

class Inverter:
    def __init__(self, strings, )

pv = Radiation(170,33.69,'San Diego','Roof mounted',shading_losses)
pv.total_annual_energy(8105)
pv.total_full_sun_hours_year(5.72)
pv.shading_losses()
print(pv)



module = CellModule(5200,64.9,6.46,54.7,5.98,327,-4,38,-0.176,0)
print(module)
module.Voltage_deviation('cold')


module.num_of_modules()

