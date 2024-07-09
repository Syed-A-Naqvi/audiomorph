from setuptools import setup, find_packages

setup(
    name='audioforge',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "matplotlib",
        "soudfile",
        "scipy",
        "librosa",
        "mpmath"
    ],
    entry_points={
        'console_scripts': [
            # 'script_name=module:function',
        ],
    },
    author='Syed Arham Naqvi',
    author_email='syedm.naqvi@ontariotechu.com',
    description='Provides functionalities for editing and augmenting audiofiles.',
    url='https://github.com/Syed-A-Naqvi/audioforge.git',  # URL to the package's repository
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
