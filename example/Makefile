# Modified from https://riptutorial.com/makefile/example/21376/building-from-different-source-folders-to-different-target-folders

# Name of the final executable
TARGET = ex

# We have 3 dirs:
SRC_DIRS := ../src ../unity ../example

# Generate the GCC includes parameters by adding -I before each source folder
INCLUDES := $(foreach dir, $(SRC_DIRS), $(addprefix -I, $(dir)))

# C source file & corresponding .o files.
SOURCES := $(foreach dir,$(SRC_DIRS),$(wildcard $(dir)/*.c))
OBJS := $(addsuffix .o, $(basename $(notdir $(SOURCES))))

test:
	@echo $(INCLUDES)
	@echo $(SOURCES)
	@echo $(OBJS)

ifeq (0, 1)	
# Set project directory one level above of Makefile directory. $(CURDIR) is a GNU make variable containing the path to the current working directory
PROJDIR := $(realpath $(CURDIR)/..)
SOURCEDIR := $(PROJDIR)/Sources
BUILDDIR := $(PROJDIR)/Build

# Create the list of directories
DIRS = Folder0 Folder1 Folder2
SOURCEDIRS = $(foreach dir, $(DIRS), $(addprefix $(SOURCEDIR)/, $(dir)))
TARGETDIRS = $(foreach dir, $(DIRS), $(addprefix $(BUILDDIR)/, $(dir)))

# Add this list to VPATH, the place make will look for the source files
VPATH = $(SOURCEDIRS)

# Define objects for all sources
OBJS := $(subst $(SOURCEDIR),$(BUILDDIR),$(SOURCES:.c=.o))

# Define dependencies files for all objects
DEPS = $(OBJS:.o=.d)

# Name the compiler
CC = gcc

# OS specific part
ifeq ($(OS),Windows_NT)
    RM = del /F /Q 
    RMDIR = -RMDIR /S /Q
    MKDIR = -mkdir
    ERRIGNORE = 2>NUL || true
    SEP=\\
else
    RM = rm -rf 
    RMDIR = rm -rf 
    MKDIR = mkdir -p
    ERRIGNORE = 2>/dev/null
    SEP=/
endif

# Remove space after separator
PSEP = $(strip $(SEP))

# Define the function that will generate each rule
define generateRules
$(1)/%.o: %.c
    @echo Building $$@
    $(CC) -c $$(INCLUDES) -o $$(subst /,$$(PSEP),$$@) $$(subst /,$$(PSEP),$$<) -MMD
endef

.PHONY: all clean directories 

all: directories $(TARGET)

$(TARGET): $(OBJS)
    echo Linking $@
    $(CC) $(OBJS) -o $(TARGET)

# Include dependencies
-include $(DEPS)

# Generate rules
$(foreach targetdir, $(TARGETDIRS), $(eval $(call generateRules, $(targetdir))))

directories: 
    $(MKDIR) $(subst /,$(PSEP),$(TARGETDIRS)) $(ERRIGNORE)

# Remove all objects, dependencies and executable files generated during the build
clean:
    $(RMDIR) $(subst /,$(PSEP),$(TARGETDIRS)) $(ERRIGNORE)
    $(RM) $(TARGET) $(ERRIGNORE)
    @echo Cleaning done ! 
endif
