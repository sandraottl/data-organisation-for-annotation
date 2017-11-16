from setuptools import setup, find_packages

setup(name='scripts',
      version='0.1.1',
      packages=find_packages(),
      install_requires=['soundfile'], 
      entry_points={
          'console_scripts': [
              'remove_overlaps = scripts.remove_overlaps:main',
              'insert_annotations = scripts.insert_annotations:main',
              'organise_timestamps = scripts.organise_timestamps:main',
              'split_videos = scripts.split_videos:main',
              'fleiss_kappa = scripts.fleiss_kappa:main',
              'create_audacity_timestamps = scripts.create_audacity_timestamps:main'
          ]
      },

      zip_safe=False
      )
