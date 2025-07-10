#ifndef NAME_TO_ENUM_H
#define NAME_TO_ENUM_H

#ifndef ARRAY_COUNT
#define ARRAY_COUNT(arr) (sizeof(arr) / sizeof(arr[0]))
#endif

/*
 * Given a string in the `var##_name` variable, find the string in the
 * `names` array and store its index into the `var` variable.
 * If the string is not found, raise a Python exception and return.
 */
#define NAME_TO_ENUM(var, names)                                               \
    {                                                                          \
        var = 0;                                                               \
        bool success = false;                                                  \
        for (size_t i = 0; i < ARRAY_COUNT(names); i++) {                      \
            if (names[i] == NULL)                                              \
                continue;                                                      \
            if (strcmp(var##_name, names[i]) == 0) {                           \
                success = true;                                                \
                var = i;                                                       \
            }                                                                  \
        }                                                                      \
        if (!success) {                                                        \
            PyErr_Format(PyExc_ValueError, "Bad " #var " name: %s",            \
                         var##_name);                                          \
            return -1;                                                         \
        }                                                                      \
    }

#endif
