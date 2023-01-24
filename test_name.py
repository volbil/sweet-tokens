from service.consensus.regex import ticker
from service import constants

def test():
    # Root checks
    assert(ticker("MIN")["valid"] == True)
    assert(ticker("MIN")["type"] == constants.TOKEN_ROOT)

    assert(ticker("MAX_ASSET_IS_31_CHARACTERS_LONG")["valid"] == True)
    assert(ticker("MAX_ASSET_IS_33_CHARACTERS_LONGT")["valid"] == False)
    assert(ticker("A_BCDEFGHIJKLMNOPQRSTUVWXY.Z")["valid"] == True)
    assert(ticker("0_12345678.9")["valid"] == True)

    assert(ticker("NO")["valid"] == False)
    assert(ticker("nolower")["valid"] == False)
    assert(ticker("NO SPACE")["valid"] == False)

    assert(ticker("_ABC")["valid"] == False)
    assert(ticker("ABC_")["valid"] == False)
    assert(ticker(".ABC")["valid"] == False)
    assert(ticker("ABC.")["valid"] == False)
    assert(ticker("AB..C")["valid"] == False)
    assert(ticker("A__BC")["valid"] == False)
    assert(ticker("A._BC")["valid"] == False)
    assert(ticker("AB_.C")["valid"] == False)

    assert(ticker("MBC")["valid"] == False)
    assert(ticker("MICROBITCOIN")["valid"] == False)

    assert(ticker("RAVEN.COIN")["valid"] == True)
    assert(ticker("RAVEN_COIN")["valid"] == True)
    assert(ticker("RVNSPYDER")["valid"] == True)
    assert(ticker("SPYDERRVN")["valid"] == True)
    assert(ticker("RAVENSPYDER")["valid"] == True)
    assert(ticker("SPYDERAVEN")["valid"] == True)
    assert(ticker("BLACK_RAVENS")["valid"] == True)
    assert(ticker("SERVNOT")["valid"] == True)

    # Sub checks
    assert(ticker("ABC/A")["valid"] == True)
    assert(ticker("ABC/A")["type"] == constants.TOKEN_SUB)

    assert(ticker("ABC/A/1")["valid"] == True)
    assert(ticker("ABC/A_1/1.A")["valid"] == True)
    assert(ticker("ABC/AB/XYZ/STILL/MAX/30/123456")["valid"] == True)

    assert(ticker("ABC//MIN_1")["valid"] == False)
    assert(ticker("ABC/")["valid"] == False)
    assert(ticker("ABC/NOTRAIL/")["valid"] == False)
    assert(ticker("ABC/_X")["valid"] == False)
    assert(ticker("ABC/X_")["valid"] == False)
    assert(ticker("ABC/.X")["valid"] == False)
    assert(ticker("ABC/X.")["valid"] == False)
    assert(ticker("ABC/X__X")["valid"] == False)
    assert(ticker("ABC/X..X")["valid"] == False)
    assert(ticker("ABC/X_.X")["valid"] == False)
    assert(ticker("ABC/X._X")["valid"] == False)
    assert(ticker("ABC/nolower")["valid"] == False)
    assert(ticker("ABC/NO SPACE")["valid"] == False)
    assert(ticker("ABC/(*#^&$%)")["valid"] == False)
    assert(ticker("ABC/AB/XYZ/STILL/MAX/30/OVERALL/1234")["valid"] == False)

    # Sub checks
    assert(ticker("ABC#AZaz09")["valid"] == True)
    assert(ticker("ABC#AZaz09")["type"] == constants.TOKEN_UNIQUE)

    assert(ticker("ABC#abc123ABC@$%&*()[]{}-_?.:")["valid"] == True)
    assert(ticker("ABC/THING#STILL_31_MAX-------")["valid"] == True)

    assert(ticker("ABC#no!bangs")["valid"] == False)
    assert(ticker("MIN#")["valid"] == False)
    assert(ticker("ABC#NO#HASH")["valid"] == False)
    assert(ticker("ABC#NO SPACE")["valid"] == False)
    assert(ticker("ABC#RESERVED/")["valid"] == False)
    assert(ticker("ABC#RESERVED~")["valid"] == False)
    assert(ticker("ABC#RESERVED^")["valid"] == False)

    # Owner checks
    assert(ticker("ABC!")["valid"] == True)
    assert(ticker("ABC!")["type"] == constants.TOKEN_OWNER)

    assert(ticker("MAX_ASSET_IS_32_CHARACTERS_LNG!")["valid"] == True)
    assert(ticker("ABC/A!")["valid"] == True)
    assert(ticker("ABC/A/1!")["valid"] == True)
    assert(ticker("ABC!")["valid"] == True)

    assert(ticker("ABC!COIN")["valid"] == False)
    assert(ticker("MAX_ASSET_IS_32_CHARACTERS_LONGT!")["valid"] == False)
    assert(ticker("ABC#UNIQUE!")["valid"] == False)


if __name__ == "__main__":
    test()
