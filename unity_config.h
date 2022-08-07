
#define TT_INCLUDE_EXTRA(...)
#define TT_BEGIN_FIXTURE(...)
#define TT_END_FIXTURE()
#define TT_DUMP_FUNC(...)
#define TT_TEST_CASE(...)
#define TT_IGNORE_TILL_EOF()

// Function to print test context on failure.
void dumpTestContext();

#define UNITY_PRINT_TEST_CONTEXT dumpTestContext



