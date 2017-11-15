# coding:utf-8
"""
author=fenglelanya
learn more

"""
from enum import Enum,unique
#unique 唯一化
@unique
class EnumQuoteApiType(Enum):
    """行情AIP类型"""
    CTP_Future_Md = 0
    LTS_Stock_Md = 1
    Fix_GuoXin_Stock_Md=2
    HengSheng_T2_Stock_Md=3
    HongHui_Stock_Md=4
    Wind_Stock_Md=5
    GuoTaiJunAn_Stock_Md = 6
    CTP_Stock_Md=7
    FeiMa_Md=8
    FeiShu_Md=9
    YiSheng_Md=10
    EM_DongFang_Finance_Md=11

@unique
class EnumTradeApiType(Enum):
    """交易API类型"""
    CTP_Future_Td = 0
    LTS_Stock_Td = 1
    Fix_GuoXin_Stock_Td=2
    HengSheng_T2_Stock_Td=3
    HongHui_Stock_Td=4
    Wind_Stock_Td=5
    GuoTaiJunAn_Stock_Td = 6
    CTP_Stock_Td=7
    FeiMa_Td=8
    FeiShu_Td=9
    YiSheng_Td=10

@unique
class EnumOrderStatusType(Enum):
    AllTraded=10
    Canceled=11
    Unknown=12
    NoTradeQueueing=13
    NotTouched=14
    Touched=15

@unique
class EnumPositionDirectionType(Enum):
    Net=11
    Long=12
    Short=13

@unique
class EnumOnRspQryInvestorPosition(Enum):
    """查询持仓回报的字段"""
    InstrumentID=1
    BrokerID=2
    InvestorID=3
    PosiDirection=4
    HedgeFlag=5
    PositionDate=6
    YdPosition=7
    Position=8
    LongFrozen=9 # 多头冻结
    ShortFrozen=10 # 空头冻结
    LongFrozenAmount=11 # 多头冻结的金额
    ShortFrozenAmount=12 # 空头冻结金额
    UseMargin=13 # 占用的保证金
    FrozenMargin=14 # 冻结的保证金
    FrozenCash=15 # 冻结的资金
    FrozenCommission=16 # 冻结的手续费
    Commission=17 # 手续费
    CloseProfit=18 # 平仓盈亏
    PositionProfit=19 # 持仓盈亏
    ExchangeID=20 # 交易所的ID
    TradingDay=21

@unique
class EnumPositionDate(Enum):
    Today=10
    History=11

@unique
class EnumIndexDataType(Enum):
    Name=10
    Code=11
    OpenPrice=12
    HightestPrice=13
    LowestPrice=14
    PreCloesPrice=15
    LastPrice=16
    Trade_Vol=17  #成交量
    Trade_Num=18  #成交额
    Amplitude_Rate = 19 #振幅
    ZhangDie_num = 20  #涨跌额
    ZhangDie_Rate = 21  #涨跌率
    Up_Time=22

@unique
class EnumStockDataType(Enum):
    Ex_Code=10
    Name=11
    Code=12
    LastPrice=13
    PreClosePrice=14
    OpenPrice=15
    Vol_Shou=16
    Out_Pan=17
    In_Pan=18
    Bid1Price=19
    Bid1Vol=20
    Bid2Price = 21
    Bid2Vol = 22
    Bid3Price = 23
    Bid3Vol = 24
    Bid4Price = 25
    Bid4Vol = 26
    Bid5Price = 27
    Bid5Vol = 28
    Ask1Price=30
    Ask1Vol=31
    Ask2Price = 32
    Ask2Vol = 33
    Ask3Price = 34
    Ask3Vol = 35
    Ask4Price = 36
    Ask4Vol = 37
    Ask5Price = 38
    Ask5Vol = 39
    Soon_ZhuBi_Traded = 40
    Up_time = 41
    ZhangDie_num=42
    ZhangDie_Rate = 43
    HightPrice=44
    LowPrice=45
    Trade_Vol_num=46
    Trade_Vol_Shou=47
    Trade_Volu_num_W=48
    Turnover_Rate=49
    PE=50
    H=51
    L=52
    Amplitude_Rate=53
    Circulation_Market_Value=54
    Market_Capitalization=55
    PB=56
    RaisinglimitPrice=57
    LimitdownPrice=58  #跌停板

@unique
class EnumExchangeIDType(Enum):
    """交易所ID"""
    IB = 49
    XBXG = 50
    INE = 51
    SSE = 65
    BOCE = 66
    CME = 67
    DCE = 68
    CME_CBT = 69
    SZSE = 70
    SGE = 71
    eCBOT = 72
    NYBOT = 73
    CFFEX = 74
    KRX = 75
    XEurex = 76
    SGXQ = 77
    TOCOM = 78
    HKEX = 79
    LME = 80
    Liffe = 81
    BMD = 82
    SHFE = 83
    SFE = 84
    ICE = 85
    DME = 86
    JPX = 87
    EURONEXT = 88
    IPE = 89
    CZCE = 90

@unique
class EnumOffsetFlagType(Enum):
    """开平仓类型"""
    Open = 48
    Close = 49
    ForceClose = 50
    CloseToday = 51
    CloseYesterday = 52
    ForceOff = 53
    LocalForceClose = 54

@unique
class EnumDirectionType(Enum):
    """买卖类型"""
    Buy = 48
    Sell = 49
    ETFPur = 50
    ETFRed = 51
    OFPur = 52
    OFRed = 53
    SFSplit = 54
    SFMerge = 55

@unique
class EnumHedgeFlagEnType(Enum):
    Speculation=1 # 投机
    Arbitrage=2  # 套利
    Hedge=3 # 套保
    Covered = 4  # 备兑

@unique
class EnumMarketDataType(Enum):
    InstrumentID=1
    ExchangeID=2
    LastPrice=3
    PreClosePrice=4
    SettlementPrice=5 # 本次结算价
    PreSettlementPrice=6 # 上次结算价
    OpenPrice=7
    HighestPrice=8
    LowestPrice=9
    Volume=10 # 成交量
    Turnover=11 # 成交金额
    UpperLimitPrice=12 # 涨停价
    LowerLimitPrice=13 # 跌停价
    UpdateTime=14 # 最后修改时间
    BidPrice1=15 # 买一
    BidVolume1=16 # 买一量
    BidPrice2=17 # 买二
    BidVolume2=18 # 买二量
    BidPrice3=19
    BidVolume3=20
    BidPrice4=21
    BidVolume4=22
    BidPrice5=23
    BidVolume5=24
    AskPrice1=25  # 卖一
    AskVolume1=26 # 卖一量
    AskPrice2=27
    AskVolume2=28
    AskPrice3=29
    AskVolume3=30
    AskPrice4=31
    AskVolume4=32
    AskPrice5=33
    AskVolume5=34
    AveragePrice=35
    TradingDay=36