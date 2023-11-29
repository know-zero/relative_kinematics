# Relative Kinematics in Anchorless Environment

Thus is a Python library for reproducing the work published in [Estimation of Relative Kinematic Parameters in Anchorless Environments](https://link-url-here.org).

## Description

* **./main:** contains the code for 
* **./output:** contains the code for 
* **./plot:** contains the code for 
* **./util:** contains the code for 

## Support and questions to the community

Ask questions using the issues section.

## Supported Platforms:

[<img src="https://www.python.org/static/community_logos/python-logo-generic.svg" height=40px>](https://www.python.org/)
[<img src="https://upload.wikimedia.org/wikipedia/commons/5/5f/Windows_logo_-_2012.svg" height=40px>](http://www.microsoft.com/en-gb/windows)
[<img src="https://upload.wikimedia.org/wikipedia/commons/8/8e/OS_X-Logo.svg" height=40px>](http://www.apple.com/osx/)
[<img src="https://upload.wikimedia.org/wikipedia/commons/3/35/Tux.svg" height=40px>](https://en.wikipedia.org/wiki/List_of_Linux_distributions)

Python 3.5 and higher

## Citation

    @Misc{gpy2014,
      author =   {{A. Mishra and R. T. Rajan}},
      title =    {{Estimation of Relative Kinematic Parameters of an
Anchorless Network}},
      howpublished = {\url{http://github.com/SheffieldML/GPy}},
      year = {2023}
    }

## Getting started:

The code is written in Python.

### Python packages:

Packages to be installed:

    conda update scipy
    sudo apt-get update
    sudo apt-get install python3-dev
    sudo apt-get install build-essential   
    conda update anaconda

### Running simulations:

Constant velocity case and comparison with the State-of-the-Art:

    python3 $DIR$/main/comp_vel.py

Constant acceleration case and comparison with the State-of-the-Art::

    python3 $DIR$/main/cnst_acc.py

Constant acceleration case and effect of Signal-to-Noise (SNR) ratio:

    python3 $DIR$/main/cnst_acc_snr.py

Appendix plots:

    python3 $DIR$/plots/travis_tests.py
    python3 $DIR$/plots/travis_tests.py

## Funding Acknowledgements

* This work is partially funded by the European Leadership Joint Undertaking (ECSEL JU), under grant agreement No 876019, the ADACORSA project - ”Airborne Data Collection on Resilient System Architectures.”
