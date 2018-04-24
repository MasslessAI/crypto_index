from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='CII',
    version='0.1.0',
    description='Crypto Index Indicator',
    long_description=long_description,
    url='massless.ai',
    author='Massless Inc.',
    author_email='info@massless.ai',
    classifiers=[
        'Development Status :: 1 - Dev',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='alternative crypto currency index',
    packages=find_packages(),
    install_requires=['pandas', 'requests', 'numpy', 'matplotlib'],
    # extras_require={  # Optional
    #     'dev': ['check-manifest'],
    #     'test': ['coverage'],
    # },
    # package_data={  # Optional
    #     'sample': ['package_data.dat'],
    # },
    # data_files=[('my_data', ['data/data_file'])],  # Optional
    # entry_points={  # Optional
    #     'console_scripts': [
    #         'sample=sample:main',
    #     ],
    # },
    # project_urls={
    #     'Website': 'https://massless.ai',
    #     'Source': 'https://github.com/massless-ai/',
    # }
)
