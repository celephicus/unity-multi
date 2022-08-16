# Hand coded as we only have a few directories.

TARGET = ex

INCLUDES := -I../src -I../unity -I.
DEPS := testOne.h ../src/unity_config.h ../unity/unity.h ../unity/unity_internals.h

CFLAGS = -std=c99 -Wall
BUILD_DIR := build
CDEFS := -DUNITY_INCLUDE_CONFIG_H

# Hack to make sure build dir exists, run before any rules. 
$(shell mkdir -p $(BUILD_DIR))

$(TARGET): $(BUILD_DIR)/unity.o $(BUILD_DIR)/test_two.o $(BUILD_DIR)/testOne.o $(BUILD_DIR)/grm_runner.o
	gcc $^ -o $@

$(BUILD_DIR):
	mkdir -p $@
	
.PHONY: clean
clean:
	rm -rf $(BUILD_DIR) $(TARGET)

# Build test harness with main(). Always runs but output file only written if changed.
$(BUILD_DIR)/grm_runner.c: test_two.c testOne.c
	../src/grm.py -o $@ -v

$(BUILD_DIR)/grm_runner.o: $(BUILD_DIR)/grm_runner.c $(DEPS)
	gcc -c $(INCLUDES) $(CFLAGS) $(CDEFS) $< -o $@


$(BUILD_DIR)/unity.o: ../unity/unity.c $(DEPS)
	gcc -c $(INCLUDES) $(CFLAGS) $(CDEFS) $< -o $@

$(BUILD_DIR)/test_two.o: test_two.c $(DEPS)
	gcc -c $(INCLUDES) $(CFLAGS) $(CDEFS) $< -o $@

$(BUILD_DIR)/testOne.o: testOne.c $(DEPS)
	gcc -c $(INCLUDES) $(CFLAGS) $(CDEFS) $< -o $@

	
