#include "unity.h"


void test_none_2_a() { TEST_ASSERT(1); }
void test_none_2_b() { TEST_ASSERT(1); }


void testScript(int x) { 
	TEST_ASSERT_EQUAL(1, x); 
}

/*
TT_BEGIN_SCRIPT()
tt = range(3)
TT_END_SCRIPT()

TT_BEGIN_SCRIPT()
for t in tt:
	add_test_case('testScript', str(t))
TT_END_SCRIPT()
*/

