from setuptools import setup, find_packages

setup(name='de_enigma_scripts',
      version='0.1.1',
      packages=find_packages(),
      install_requires=['soundfile'], 
      entry_points={
          'console_scripts': [
              'remove_overlaps = de_enigma_scripts.remove_overlaps:main',
              'insert_annotations = de_enigma_scripts.insert_annotations:main',
              'organise_timestamps = de_enigma_scripts.organise_timestamps:main',
              'split_videos = de_enigma_scripts.split_videos:main',
              'fleiss_kappa = de_enigma_scripts.fleiss_kappa:main'
          ]
      },

      zip_safe=False
      )
