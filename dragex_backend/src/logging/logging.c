#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "logging.h"

static char *log_prolog_prefix = "[DragEx] ";

#define log_internal(format, ...)                                              \
    _log_internal(__FILE__, __LINE__, __FUNCTION__, format, ##__VA_ARGS__)

__attribute__((format(printf, 4, 5))) static void
_log_internal(const char *file, int line, const char *function,
              const char *format, ...) {
    fprintf(stderr, "%s%s:%d %s INTERNAL ", log_prolog_prefix, file, line,
            function);

    va_list ap;
    va_start(ap, format);
    vfprintf(stderr, format, ap);
    va_end(ap);

    fprintf(stderr, "\n");
}

static int snprintf_prolog(char *buf, size_t maxlen, const char *file, int line,
                           const char *function, enum log_level level) {
    static const char *level_names[] = {
        [LOG_LEVEL_TRACE] = "TRACE", [LOG_LEVEL_DEBUG] = "DEBUG",
        [LOG_LEVEL_INFO] = "INFO",   [LOG_LEVEL_WARN] = "WARN",
        [LOG_LEVEL_ERROR] = "ERROR", [LOG_LEVEL_FATAL] = "FATAL",
    };

    return snprintf(buf, maxlen, "%s%s:%d %s %s ", log_prolog_prefix, file,
                    line, function, level_names[level]);
}

static int snprintf_epilog(char *buf, size_t maxlen) {
    return snprintf(buf, maxlen, "\n");
}

void _log(const char *file, int line, const char *function,
          enum log_level level, const char *format, ...) {
    // Count characters

    int n_prolog = snprintf_prolog(NULL, 0, file, line, function, level);

    if (n_prolog < 0) {
        log_internal("snprintf_prolog error");
        return;
    }

    va_list ap;

    va_start(ap, format);
    int n_message = vsnprintf(NULL, 0, format, ap);
    va_end(ap);

    if (n_message < 0) {
        log_internal("vsnprintf message error");
        return;
    }

    int n_epilog = snprintf_epilog(NULL, 0);

    if (n_epilog < 0) {
        log_internal("snprintf_epilog error");
        return;
    }

    int buf_len = n_prolog + n_message + n_epilog + 1;
    char *buf = malloc(buf_len);

    if (buf == NULL) {
        log_internal("malloc failed");
        return;
    }

    // Print to buf

    snprintf_prolog(buf, n_prolog + 1, file, line, function, level);

    va_start(ap, format);
    vsnprintf(buf + n_prolog, n_message + 1, format, ap);
    va_end(ap);

    snprintf_epilog(buf + n_prolog + n_message, n_epilog + 1);

    // Print

    printf("%s", buf);

    free(buf);
}
