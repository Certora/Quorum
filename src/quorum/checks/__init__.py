from .diff import DiffCheck
from .global_variables import GlobalVariableCheck
from .new_listing import NewListingCheck
from .price_feed import PriceFeedCheck
from .review_diff import ReviewDiffCheck

all = [DiffCheck, ReviewDiffCheck, GlobalVariableCheck, PriceFeedCheck, NewListingCheck]
