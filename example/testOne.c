#include "unity.h"

TT_BEGIN_INCLUDE()
#include "testOne.h"
TT_END_INCLUDE()

void test_none_1_a() { TEST_ASSERT(1); }
void test_none_1_b() { TEST_ASSERT(1); }

TT_BEGIN_FIXTURE(setupOne)		// Setup only.
void test_setup() { TEST_ASSERT(1); }
TT_END_FIXTURE();

void test_none_1_c() { TEST_ASSERT(1); }

TT_BEGIN_FIXTURE(NULL, dumpOne)
void test_dump_ok() { TEST_ASSERT(1); }
void test_dump_fail() { TEST_ASSERT(0); }
TT_END_FIXTURE()

TT_BEGIN_FIXTURE(setupOne, NULL, teardownOne);		// Setup & teardown.
void test_setup_teardown() { TEST_ASSERT(1); }

TT_BEGIN_FIXTURE(NULL, NULL, teardownOne)		// Teardown only.
void test_teardown() { TEST_ASSERT(1); }
TT_END_FIXTURE();

void test_1f(int x) { TEST_ASSERT(x); }

TT_TEST_CASE(test_1f(0));
TT_TEST_CASE(test_1f(1));

TT_IGNORE_FROM_HERE()

void test_1_ignored() { TEST_ASSERT(0); }

void dumpOne() {
	UnityPrint("Dump dumpOne.");
}
void setupOne() {
	UnityPrint("Setup dumpOne.");
}
void teardownOne() {
	UnityPrint("Teardown dumpOne.");
}


