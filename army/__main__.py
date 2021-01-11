#!/usr/bin/env python3
from army import main

# class Option():
#     pass
# 
# class Command():
#     def set_callback(self, callback):
#         print("callback:", callback)
# 
#     def option(self):
#         pass
#     
# class Group():
#     def toto(self):
#         print("toto")
# 
# class Parser():
#     pass
# 
# def parser(func):
#     print(f"-->> parser", func)
# #     def wrapper():
# #         print("---", obj)
# #         if obj is list:
# #             return [Parser, *obj]
# #         return [Parser(), obj]
# #     return wrapper
#     
# def group(name):
#     print(f"-->> group {name}")
#     def wrapper(obj):
#         print("---", obj)
#         if isinstance(obj, list):
#             return [Group, *obj]
#         return [Group(), obj]
#     return wrapper
# 
# def command(name):
#     print(f"-->> command {name}")
#     def wrapper(obj):
#         print("---", obj)
#         if isinstance(obj, list):
#             return [Command, *obj]
#         return [Command(), obj]
#     return wrapper
# 
# def option(name):
#     print(f"-->> option {name}")
#     def wrapper(obj):
#         print("---", obj)
#         if isinstance(obj, list):
#             return [Option, *obj]
#         return [Option(), obj]
#     return wrapper
# 
# print("-------")
# print(type(*[Option, "aaa"]))
# 
# @parser
# @group("g")
# @command("c")
# @option("help")
# @option("verbose")
# def test():
#     pass


if __name__ == "__main__":
#     test()

    main()
