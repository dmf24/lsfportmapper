from setuptools import setup

setup(name='lsfportmapper',
            version='0.0.1',
            description='Tool to register cluster ports from LSF for a content switch.  Requires dmf24 pyscripting library',
            url='http://github.com/dmf24/lsfportmapper',
            author='Doug Feldmann',
            author_email='doug@feldmann.com',
            license='MIT',
            packages=['lsfportmapper'],
            zip_safe=False)
