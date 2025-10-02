"""Train station constants"""

from dataclasses import dataclass


@dataclass
class StationInfo:
    name: str
    code: str


# KTX 역 정보
KTX_STATIONS = [
    StationInfo("서울", "NAT010000"),
    StationInfo("용산", "NAT010415"),
    StationInfo("광명", "NAT010754"),
    StationInfo("천안아산", "NAT011668"),
    StationInfo("오송", "NAT011072"),
    StationInfo("대전", "NAT011426"),
    StationInfo("김천구미", "NAT012055"),
    StationInfo("동대구", "NAT013271"),
    StationInfo("경주", "NAT013502"),
    StationInfo("울산", "NAT013707"),
    StationInfo("부산", "NAT014445"),
    StationInfo("공주", "NAT011895"),
    StationInfo("익산", "NAT012296"),
    StationInfo("정읍", "NAT012355"),
    StationInfo("광주송정", "NAT012425"),
    StationInfo("목포", "NAT012489"),
]

# SRT 역 정보
SRT_STATIONS = [
    StationInfo("수서", "0551"),
    StationInfo("동탄", "0552"),
    StationInfo("평택지제", "0553"),
    StationInfo("천안아산", "0554"),
    StationInfo("오송", "0555"),
    StationInfo("대전", "0020"),
    StationInfo("공주", "0514"),
    StationInfo("익산", "0030"),
    StationInfo("정읍", "0033"),
    StationInfo("광주송정", "0036"),
    StationInfo("목포", "0041"),
    StationInfo("김천구미", "0507"),
    StationInfo("서대구", "0508"),
    StationInfo("동대구", "0015"),
    StationInfo("신경주", "0509"),
    StationInfo("울산", "0509"),
    StationInfo("부산", "0020"),
]