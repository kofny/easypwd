#pragma once

#include <cstdio> // EOF 的定义
#include <string> // string 类型的支持
#include <cassert> // assert 函数定义
#include <sys/stat.h> // 读取文件状态
#include <vector> // 读写vector

#define inputBuffSize (67108864) // 输入缓冲区大小 64MB
#define outputBuffSize (67108864) // 输入缓冲区大小 64MB

namespace FastIO { // 由于头文件中可以定义内联函数, 因此将FastIO定义在头文件中便于使用
    // 快速输入
    namespace in {
        char buff[inputBuffSize], *ptr = NULL, *pend = NULL;
        FILE *stream = NULL;
        int filesize, readsize, itemsize, maxcnt, maxbytes; // 文件大小字节数, 已读字节数

        // 指定文件路径, 并根据文件头获取文件大小
        inline int getsize(const char *path) {
            struct stat statbuff;
            stat(path, &statbuff);
            return statbuff.st_size;
        }

        // 初始化 Fast in 参数
        //      (const char*) path: 文件路径
        //      (const char*) mode: 文件打开模式
        //   (const int) element_size=1: 文件读取的块大小, 默认为 1 字节, 缓冲区大小为 64M
        inline void init(const char *path, const char *mode = "rb", const int element_size = 1) {
            assert((stream == NULL) && (stream = fopen(path, mode)) != NULL);
            filesize = getsize(path);
            readsize = 0;
            itemsize = element_size;
            maxcnt = inputBuffSize / element_size; // buffer 整块读取时可容纳的最大块数
            maxbytes = (inputBuffSize / element_size) * element_size; // buffer 整块读取时可容纳的最大字节数
            ptr = pend = NULL;
        }

        // 初始化 Fast in 参数
        //      (const string) path: 文件路径
        //      (const char*) mode: 文件打开模式
        //   (const int) element_size=1: 文件读取的块大小, 默认为 1 字节, 缓冲区大小为 64M
        inline void init(const std::string &path, const char *mode = "rb", const int element_size = 1) {
            init(path.c_str(), mode, element_size);
        }

        // 读取流 stream 中的下一个字符, 当缓冲区内容读取完毕后进行下一次I/O
        // 返回EOF(-1)表示读取完成, 返回-2表示达到文件尾之前出错
        inline char nextchar() {
            if (readsize >= filesize) return EOF; // 文件读取完成
            if (ptr >= pend) {
                int realbytes = itemsize * fread(buff, itemsize, maxcnt, stream); // fread返回实际读取的块数
                if (realbytes < maxbytes && realbytes + readsize < filesize) return -2; // 读取出错 返回-2
                ptr = buff; // 重置首尾指针
                pend = buff + realbytes;
            }
            return readsize++, *ptr++;
        }

        // 读取一个字符, 读取失败则不改变char, 否则改变char c的值
        inline bool read(char &c) {
            char tmp = nextchar(); // tmp == -1 (EOF): 到达文件尾, tmp == -2: 读取出错
            return tmp < 0 ? false : (c = tmp, true);
        }

        // 读取一个整数, true 表示读取成功, false 表示读取失败
        inline bool read(int &x) {
            char c = nextchar();
            while (c >= 0 && c != '-' && (c < '0' || c > '9')) c = nextchar();
            if (c < 0) return false; // c == -1 (EOF): 到达文件尾, c == -2: 读取出错
            int sign = (c == '-') ? -1 : 1; // 正负号
            x = (c == '-') ? 0 : c - '0';
            while (c = nextchar(), c >= '0' && c <= '9') x = x * 10 + c - '0';
            x *= sign;
            return true;
        }

        // 读取一个长度为 n 的整数 tuple, 如 (1, -2, 31), true 表示读取成功, false 表示失败
        inline bool read(int *p, const int n) {
            for (int *end = p + n; p < end; ++p) if (!read(*p)) return false;
            return true;
        }

        // 关闭输入流释放资源
        inline int close() {
            int ret = fclose(stream);
            filesize = readsize = itemsize = maxcnt = 0;
            ptr = pend = NULL;
            stream = NULL;
            return ret;
        }
    }

    // 快速输出
    namespace out {
        char buff[outputBuffSize], *ptr = NULL, *pend = NULL;
        FILE *stream = NULL;
        int itemsize, maxbytes; // 写入的块大小, 整块存放时缓存的最大字节数

        // 初始化 Fast out 参数
        //      (const char*) path: 文件路径
        //      (const char*) mode: 文件打开模式
        //   (const int) element_size=1: 文件读取的块大小, 默认为 1 字节, 缓冲区大小为 64M
        inline void init(const char *path, const char *mode = "wb", const int element_size = 1) {
            assert(stream == NULL && (stream = fopen(path, mode)) != NULL);
            itemsize = element_size;
            maxbytes = (outputBuffSize / element_size) * element_size; // 输出缓冲的最大字节数
            ptr = buff;
            pend = buff + maxbytes;
        }

        inline void init(const int element_size = 1) {
            stream = stdout;
            itemsize = element_size;
            maxbytes = (outputBuffSize / element_size) * element_size; // 输出缓冲的最大字节数
            ptr = buff;
            pend = buff + maxbytes;
        }

        // 初始化 Fast out 参数
        //      (const string) path: 文件路径
        //      (const char*) mode: 文件打开模式
        //   (const int) element_size=1: 文件读取的块大小, 默认为 1 字节, 缓冲区大小为 64M
        inline void init(const std::string &path, const char *mode = "wb", const int element_size = 1) {
            init(path.c_str(), mode, element_size);
        }

        // 冲刷缓冲区
        inline void flush() {
            fwrite(buff, itemsize, (ptr - buff) / itemsize, stream);
            ptr = buff; // 调整首指针
            fflush(stream);
        }

        // 写入一个字符到文件中
        inline void write(const char &c) {
            if (ptr >= pend) flush();
            *ptr++ = c;
        }

        // 写一个字符串到文件中
        inline void write(const char *s) {
            for (; *s; ++s) write(*s); // 读取到字符串尾部时 '\0' ASCII为0
        }

        // 写一个 string 类型的字符串到文件中
        inline void write(const std::string &s) {
            write(s.c_str());
        }

        // 写入一个整数到文件中
        inline void write(int x) {
            char buf[20], *p = buf;
            if (x == 0) write('0');
            if (x < 0) write('-'), x = -x;
            while (x > 0) *p++ = x % 10 + '0', x /= 10;
            while (p > buf) write(*--p);
        }

        template<typename T>
        // 写入一个含有n个元素的tuple到文件中 如 (32, -1, 14), drop_end 控制是否输出 end 符号
        inline void write(const T *p, int n, const char *left = "(", const char *right = ")",
                          const char *split = ", ", const char *end = "\n", const bool drop_end = false) {
            write(left);
            while (--n) write(*p++), write(split);
            write(*p);
            write(right);
            if (!drop_end) write(end);
        }

        template<typename T>
        // 写入一个使用 vector 存储的 tuple
        inline void write(std::vector<T> &vec, const char *left = "(", const char *right = ")",
                          const char *split = ", ", const char *end = "\n", const bool drop_end = false) {
            int n = vec.size() - 1;
            write(left);
            for (int i = 0; i < n; ++i) write(vec[i]), write(split);
            write(vec[n]);
            write(right);
            if (!drop_end) write(end);
        }

        // 冲刷缓冲并关闭输出流释放资源
        inline int close() {
            if (ptr > buff) flush();
            int ret = fclose(stream);
            ptr = pend = NULL;
            stream = NULL;
            return ret;
        }
    }
}