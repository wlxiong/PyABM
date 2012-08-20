# or we can use:
#   python -m cProfile -s time -o profile.log tests.py <args>

if __name__ == '__main__':
    import cProfile
    import pstats
    import tests
    import sys
    import os
    # turn off debug messages
    sys.stdout = open(os.devnull, 'w')
    # run profiler
    cProfile.run('tests.main()', 'profile.log')
    # restore the stdout
    sys.stdout.close()
    sys.stdout = sys.__stdout__
    p = pstats.Stats('profile.log')
    p.strip_dirs().sort_stats(-1)
    p.sort_stats('time').print_stats(20)
    