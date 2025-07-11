#ifndef DRAGEX_LOGGING
#define DRAGEX_LOGGING

#include <stdbool.h>

#if !defined(__GNUC__) && !defined(__attribute__)
#define __attribute__(x)
#endif

enum log_level {
    LOG_LEVEL_NONE,
    LOG_LEVEL_TRACE,
    LOG_LEVEL_DEBUG,
    LOG_LEVEL_INFO,
    LOG_LEVEL_WARN,
    LOG_LEVEL_ERROR,
    LOG_LEVEL_FATAL
};

__attribute__((format(printf, 5, 6))) void _log(const char *file, int line,
                                                const char *function,
                                                enum log_level level,
                                                const char *format, ...);

#define log(level, format, ...)                                                \
    _log(__FILE__, __LINE__, __FUNCTION__, level, format, ##__VA_ARGS__)

#define log_trace(format, ...) log(LOG_LEVEL_TRACE, format, ##__VA_ARGS__)
#define log_debug(format, ...) log(LOG_LEVEL_DEBUG, format, ##__VA_ARGS__)
#define log_info(format, ...) log(LOG_LEVEL_INFO, format, ##__VA_ARGS__)
#define log_warn(format, ...) log(LOG_LEVEL_WARN, format, ##__VA_ARGS__)
#define log_error(format, ...) log(LOG_LEVEL_ERROR, format, ##__VA_ARGS__)
#define log_fatal(format, ...) log(LOG_LEVEL_FATAL, format, ##__VA_ARGS__)

bool set_log_file(const char *path);
void log_flush(void);

#endif
