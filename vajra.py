# -*- coding: utf-8 -*-
"""
BSD 3-Clause License

Copyright (c) 2019, Varush Varsha
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import numpy
import pandas
import sys
import scipy.stats

import matplotlib.pyplot as plt
#for glossy graphing capabilities
plt.style.use("fivethirtyeight")
plt.rcParams.update({"font.family": "MathJax_Fraktur"})
plt.rcParams.update({"font.size": 12})
plt.rcParams.update({"lines.linewidth": 0.55})

import warnings
warnings.simplefilter(action="ignore", category=FutureWarning)

prefix = "./.cache/"

def getDF(instrumentName):
    """clean and fetch the dataframe from ./.cache """
    try:
        df = pandas.DataFrame.from_csv(prefix+instrumentName+".csv")
        df.dropna(how="any", inplace=True)
        return df
    except (FileNotFoundError, ValueError):
        raise FileNotFoundError

def correlation(instrumentOne, instrumentTwo):
    """ correlation between two given instruments"""
    df  = getDF(instrumentOne)
    dg  = getDF(instrumentTwo)
    dfx = df["Adj Close"]
    dgx = dg["Adj Close"]
    mxx = max(len(dfx), len(dgx))
    mnn = min(len(dfx), len(dgx))
    dfr = mxx - mnn
    if mxx == len(dfx):
        fx = dfx[dfr:mxx]/dfx[dfr]
        gx = dgx/dgx[0]
        return scipy.stats.pearsonr(fx.values, gx.values)[0]
    else:
        fx = dfx/dfx[0]
        gx = dgx[dfr:mxx]/dgx[dfr]
        return scipy.stats.pearsonr(fx.values, gx.values)[0]

def absoluteLog(x):
    """simply return 0.0 if x is negative"""
    return numpy.log(x) if x > 0.0 else 0.0

def printer(instrumentName, correlationValue, percentage, fullName):
    """ printing facility """
    print("For {3:25s}[{0:5s}] the correlation is {1:5.12f}, %age of Portfolio {2:5.12f}".format(instrumentName,
                                                                                                  correlationValue,
                                                                                                  percentage,
                                                                                                  fullName))
def between(a, b, x):
    """strict checking for a < x < b [the syntax is necessary to negate the compiler/architecture idiosyncrasies]"""
    if x > a:
        if x < b:
            return True
        else:
            return False
    else:
        return False

def fromLen(num):
    l = len(num)
    if l <= 5+1:
        return num
    elif l == 7:
        return num[0] + " million"
    elif l == 8:
        return num[0:2] + " million"
    elif l == 9:
        return num[0:3] + " million"
    elif l == 10:
        return num[0] + " billion " + num[1:3] + " million"
    elif l == 11:
        return num[0:2] + " billion " + num[2:4] + " million"
    elif l == 12:
        return num[0:3] + " billion " + num[3:5] + " million"
    else:
        pass

def getInWords(num):
    numString = str(num).split('.')[0]
    return fromLen(numString)

def exponentialCompromisedVersion(instrumentName):
    """The so-called compromised version of the exponential stability test"""
    df = 0
    try:
        df = getDF(instrumentName)
    except FileNotFoundError:
        pass
    print(type(df))
    if type(df) == pandas.core.frame.DataFrame:
        y1 = df["Adj Close"][0]
        y2 = df["Adj Close"][-1]
        eX = numpy.linspace(numpy.log(y1), numpy.log(y2), len(df))
        x1 = eX[0]; x2 = eX[-1]
        m1 = (y2-y1)/(x2-x1)
        ln = numpy.array([m1*(k-x1)+y1 for k in eX])
        lowerBounds = pandas.DataFrame(data=numpy.exp(eX), index=df.index)
        upperBounds = pandas.DataFrame(data=ln+(ln-numpy.exp(eX)), index=df.index)
        plt.figure()
        plt.title(instrumentName, fontname="MathJax_TypeWriter", fontsize=12)
        plt.plot(df["Adj Close"], color="RoyalBlue")
        plt.plot(lowerBounds, color="Purple", linewidth="0.55")
        plt.plot(pandas.DataFrame(data=ln, index=df.index), color="Purple", linewidth="0.55")
        plt.plot(upperBounds, color="Purple", linewidth="0.55")
        plt.show()
        dv = numpy.ravel(df["Adj Close"].values)
        ub = numpy.ravel(upperBounds.values)
        lb = numpy.ravel(lowerBounds.values)
        counter = 0
        for k, l in enumerate(dv):
            if between(lb[k], ub[k], l) is True:
                counter = counter + 1
            else:
                pass
        return (counter*100.0)/len(dv), correlation("TENCENT", instrumentName)
    else:
        return 0
                

def main():
    """ the pointless placeholder for independent testing"""
    print(exponentialCompromisedVersion("AMZN"))

if __name__ == "__main__":
    main()
