from setuptools import setup, find_packages

name = 'configmng'
version = "0.0.1"
setup(
    name=name,
    version=version,
    license='bsd-3-clause',
    url='https://github.com/christian-oreilly/{}.git'.format(name),
    download_url="https://github.com/christian-oreilly/{name}/archive/v{version}.tar.gz".format(name=name,
                                                                                                version=version),
    author="Christian O'Reilly",
    author_email='christian.oreilly@gmail.com',
    description='Light-weight package to manage computationally-intensive processing pipelines using SLURM.',
    packages=find_packages(),    
    install_requires=["numpy", "pyyaml", "pykwalify", "pytest"],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development',
        'License :: OSI Approved',  # Again, pick a license
        'Programming Language :: Python :: 3',  # Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
)

