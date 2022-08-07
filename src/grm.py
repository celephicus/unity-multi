#!/usr/bin/env python3

LICENCE = '''
Copyright Tom Harris 2022

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import re, sys, os, glob, argparse, functools, collections

SCRIPT_NAME = os.path.splitext(os.path.basename(sys.argv[0]))[0]

RUNNER_LEADER_STR = f'/* This file is autogenerated by {SCRIPT_NAME} -- do not edit. */'
DEFAULT_OUTPUT_FILE = 'grm_runner.c'
DEFAULT_INPUT_FILE = 'test*.c'

DEFAULT_STANDARD_INCLUDES = """\
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>

#include "unity.h"
"""

opt_parser = argparse.ArgumentParser(prog=SCRIPT_NAME,
  description='Generate test runner source file for Unity from multiple test files.')
opt_parser.add_argument('--verbose', '-v', action='store_true',  help='print lots of details')
opt_parser.add_argument('--licence', action='store_true',  help='show licence')
opt_parser.add_argument('--output', '-o', default=DEFAULT_OUTPUT_FILE,
  help=f"output file, defaults to `{DEFAULT_OUTPUT_FILE}'")
opt_parser.add_argument('files', default=[DEFAULT_INPUT_FILE], nargs='*',
  help="input file(s), may include globs, defaults to `test*.c'")
opt_parser.add_argument('--no-default-includes', '-n', action='store_true',
  help="do NOT add default #include's at start of output file")

opt_args = opt_parser.parse_args()
verbose = opt_args.verbose

# Dict containing values for output file.
rundict = {}

def exit(msg):
	sys.exit(msg)
def message(msg, **kwargs):
	if verbose: print(msg, **kwargs)

# Print licence.
if opt_args.licence:
	sys.exit(LICENCE)

# Check for overwriting a file not previously autogenerated (we've all done this...)
try:
	with open(opt_args.output, 'rt') as f:
		message(f"Output file `{opt_args.output}' exists... ")
		if RUNNER_LEADER_STR not in f.read(512):
			exit(f"""\
Output file `{opt_args.output}' exists and might not be previously generated by
this script. Delete it and retry.
""")
except OSError:
	message(f"Previous output file `{opt_args.output}' NOT FOUND.")

# Get list of standard includes that are included in the output file by default.
rundict['STANDARD_INCLUDES'] = ('/* None */' if opt_args.no_default_includes else DEFAULT_STANDARD_INCLUDES).strip()

# Regex to scrape test function declarations
# WARNING: I am not writing a generic "C" parser so do not go overboard on the functions. In particular keep it all
# on one line. 'void test_foo(void)' will work just fine.
reTestFunction = re.compile(r"""
  void 		# Return type void.
  \s+ 		# Whitespace.
  (test\w+) # Function name .
  \s*\(\s* 	# Possible whitespace, opening bracket, more possible whitespace.
  ([^)]*?) 	# Possible arguments.
  \)\s* 	# Possible whitespace & closing bracket.
""", re.X)

# Include file list.
extra_includes = []

# Process all input files, in case we see a number of glob patterns. Note that files are processed in alphabetical order.
input_files = sorted(functools.reduce(lambda x,y:x+y, [glob.glob(f) for f in opt_args.files], []))
if not input_files:
	exit("No input files!")

test_funcs = collections.OrderedDict()
test_run = []
def add_test(func_name, func_descr, func_lineno):
	global test_run
	test_run.append(f'do_run_test({func_name}, "{func_descr}", {func_lineno});')

fixture_funcs = collections.OrderedDict() # No ordered set:(
stub_num = 0
test_stubs = []

# These are like diversions in m4, they process complete lines of input. There may be at most one active at a time.
line_proc = None

block_includes = []
def line_proc_block_includes(ln):
	block_includes.append(ln)

test_case_data = []
def line_proc_test_case_data(ln):
	if not re.match(r'/\*|\*/|#if\s*0|#endif', ln):
		test_case_data.append(ln)

def add_test_case(test_func, test_args):
	global stub_num, num_tests
	if test_func not in test_funcs:
		exit(f"Macro {macro}:{fn}, line {lineno} references an unknown test function `{test_func}'.")
	test_stub_name = f'{test_func}_stub_{stub_num}'
	stub_num += 1
	test_stub_body = f'{test_func}({test_args})'
	descr = test_stub_body.replace('\\', '\\\\').replace('"', r'\"') # repr(test_stub_body.replace(r'\"', r'\\\^').replace(r'\\\^', r'\\\"')
	add_test(test_stub_name, descr, lineno)
	test_stubs.append(f'static void {test_stub_name}(void) {{ {test_stub_body}; }}')
	num_tests += 1

for fn in input_files:
	message(f"Processing input file `{fn}'...", end='')
	fixture = None
	num_tests = 0
	line_proc = None
	script_globals = {'add_test_case': add_test_case}

	try:
		with open(fn, 'rt') as f:
			src = f.read()
	except OSError:
		exit(f"\nError reading input file `{fn}'.")

	test_run.append('')
	test_run.append(f'UnitySetTestFile("{fn}");')

	for lineno, ln in enumerate(src.splitlines()): # Iterate over all lines.

		m = re.match(r'''
		  \s*		# Leading whitespace.
		  (TT_BEGIN_FIXTURE|TT_END_FIXTURE|TT_TEST_CASE|TT_IGNORE_FROM_HERE|TT_BEGIN_INCLUDE|TT_END_INCLUDE|TT_BEGIN_SCRIPT|TT_END_SCRIPT)
		  \s*\(		# Space + open bracket.
		  (.*)		# Args.
		  \)		# Closing bracket.
		  ;?		# Trailing `;' ignored.
		  \s*$		# Whitespace only.
		''', ln, re.X | re.S)
		if m:
			macro, raw_args = m.groups()
			args = [x.strip() for x in raw_args.split(',')]

			if macro == 'TT_IGNORE_FROM_HERE': # Ignore the rest of this file.
				message(f" ignoring after line {lineno}...", end='')
				break
			elif macro == 'TT_BEGIN_INCLUDE': # Start copy a block into the output file.
				if line_proc:
					exit("TT_BEGIN_INCLUDE() read whilst already in a TT include block.")
				line_proc = line_proc_block_includes
			elif macro == 'TT_END_INCLUDE': # End copy a block into the output file.
				if line_proc != line_proc_block_includes:
					exit("TT_END_INCLUDE() read whilst not in a TT include block.")
				line_proc = None
			elif macro == 'TT_BEGIN_SCRIPT':
				if line_proc: exit(f"Unexpected `{macro}'.")
				line_proc = line_proc_test_case_data
			elif macro == 'TT_END_SCRIPT':
				if line_proc != line_proc_test_case_data: exit(f"Unexpected `{macro}'.")
				line_proc = None
				script = '\n'.join(test_case_data)
				exec(script, script_globals)
				test_case_data = []
			elif macro == 'TT_BEGIN_FIXTURE': # Three options: (setUp(, (setUp, dumpContext), (setUp, dumpContext)
				if len(args) not in range(1,4):
					exit(f"Macro {macro}, {fn}, line {lineno} requires 1 or 2 arguments.")
				fixture = (args + ['NULL'] * 2)[:3]
				test_run.append('registerFixture({0});'.format(', '.join(fixture)))
				for f in fixture:
					if f != "NULL":
						fixture_funcs[f] = None
			elif macro == 'TT_END_FIXTURE':
				test_run.append('registerFixture(NULL, NULL, NULL);')
				fixture = None
			elif macro == 'TT_TEST_CASE':
				m = re.match(r'(\w+)\((.+)\)\s*$', raw_args)
				if not m:
					exit(f"Macro `{ln}' needs to be like {macro}(func(args))")
				test_func, test_args = m.groups()
				add_test_case(test_func, test_args)
			else:
				message(f" Unknown macro {macro}.")
		else:
			# Grab test files...
			m = reTestFunction.search(ln)
			if m:
				test_func, test_args = m.groups()
				if test_func in test_funcs:
					exit(f"Duplicate test function {test_func}, {fn}, {lineno}.")

				# Looks like a test function definition: void f(void), so call it.
				if test_args in ('', 'void'):
					add_test(test_func, test_func, lineno)

				# Add to list to generate a declaration.
				test_funcs[test_func] = test_args
				num_tests += 1
			else:		# Not a test file...
				if line_proc:
					line_proc(ln)

	message(f" found {num_tests} test{'s' if num_tests != 1 else ''}.")
	if fixture:
		test_run.append('registerFixture(NULL, NULL, NULL);')

# Write output file.
TEMPLATE_RUNNER = '''\
$RUNNER_LEADER_STR

#ifndef UNITY_INCLUDE_CONFIG_H
#error "Must define UNITY_INCLUDE_CONFIG_H."
#endif

/*** Standard includes. ***/
$STANDARD_INCLUDES

/*** Stuff copied from test files (should be #include's, declarations & macros only) ***/
$COPY_BLOCKS

/*** External test functions scraped from test files. ***/
$TEST_FUNCTION_DECLS

/*** Fixture & dump functions from test files. ***/
$FIXTURE_FUNCTION_DECLS

/* Declare test stubs. */
$TEST_CASE_DEFS

/*** Extra Unity support. ***/

/* Functions for setup, diagnostics dump on a test failure & teardown. */
typedef void (*fixture_func_t)(void);
static fixture_func_t setUp_func, dump_func, tearDown_func;
void registerFixture(fixture_func_t setup, fixture_func_t dumper, fixture_func_t teardown) {
	setUp_func = setup;
	dump_func = dumper;
	tearDown_func = teardown;
}

void setUp() { if (setUp_func) setUp_func(); }
void dumpTestContext() { if (dump_func) dump_func(); }
void tearDown() { if (tearDown_func) tearDown_func(); }

static void do_run_test(UnityTestFunction func, const char* name, int line_num) {
#ifdef UNITY_USE_COMMAND_LINE_ARGS
    if (!UnityTestMatches())
        return;
#endif
	UnityDefaultTestRun(func, name, line_num);
}

int main(int argc, char** argv) {
/*
	int rc_parse = UnityParseOptions(argc,argv);
	if (rc_parse != 0)
		return rc_parse;
*/
  UnityBegin("");
$TESTS
  return UnityEnd();
}

/*
$TEST_CASE_DATA
*/
'''

rundict['RUNNER_LEADER_STR'] = RUNNER_LEADER_STR
rundict['TEST_FUNCTION_DECLS'] = '\n'.join([f'void {func}({args});' for func, args in test_funcs.items()])
rundict['FIXTURE_FUNCTION_DECLS'] = '\n'.join([f'void {f}(void);' for f in fixture_funcs.keys()]) if fixture_funcs else '/* None */'
rundict['COPY_BLOCKS'] = '\n'.join(block_includes)
rundict['TEST_CASE_DATA'] = '\n'.join(test_case_data)
rundict['TEST_CASE_DEFS'] = '\n'.join(test_stubs)
rundict['TESTS'] = ''.join([f'  {x}\n' for x in test_run])

try:
	with open(opt_args.output, 'rt') as f:
		old_runner = f.read()
except OSError:
	old_runner = None

new_runner = re.sub(r'\$(\w+)', lambda m: rundict[m.group(1)], TEMPLATE_RUNNER)
if new_runner == old_runner:
	message("Skipped writing output file as identical to existing file.")
else:
	try:
		with open(opt_args.output, 'wt') as f:
			f.write(new_runner)
			message(f"Wrote output file `{opt_args.output}'...")
	except OSError:
		exit(f"Can't write output file `{opt_args.output}'.")


