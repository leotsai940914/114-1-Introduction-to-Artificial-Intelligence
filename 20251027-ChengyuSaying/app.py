import random
from fastmcp import FastMCP

mcp = FastMCP(name="chengyu_say_server")

@mcp.tool
def random_pic_chengyu_saying() -> str:
    """Random return a chengyu's saying."""

    chengyu_say_list = [
        "南無大慈大悲救苦救難不救我",
        "南無戰鬥陀螺",
        "南無觀世input薩,求output",
        "北五北六北七",
        "先做再說，少講幹話",
    ]

    chengyu_say_pick_result = random.choice(chengyu_say_list)
    return f"晟郁說：{chengyu_say_pick_result}"

if __name__ == "__main__":
    mcp.run(transport="sse", port=5002)
    # mcp.run(transport="stdio")