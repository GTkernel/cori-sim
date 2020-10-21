import numpy as np

class Page:
  def __init__(self, id):
    self.id = id
    self.req_ids = []
    self.pc_ids = []
    self.reuse_dist = []
    self.oracle_counts_ep = []
    self.counts_ep = []
    self.loc_ep = []
    
  def increase_cnt(self, ep):
    self.counts_ep[ep] += 1

class AddressSpace:
  def __init__(self):
    self.page_list = []
    self.num_pages = 0
    self.reqs_l1_pages = []
    self.l1_ratio = 0
    self.l1_pages = 0
    self.lru_list = []
    self.policy = []
    self.num_pages_misplaced = 0

  def populate(self, traffic):
    # init space
    self.num_pages = traffic.num_pages
    for page_id in range(self.num_pages):
      page = Page(page_id)
      self.page_list.append(page)
    # reqs per page
    for req in traffic.req_seq:
      page = self.page_list[req.page_id]
      page.req_ids.append(req.id)
    # reuse distance
    for page in self.page_list:
      page.reuse_dist = np.diff(np.array(page.req_ids))

  def init_cnts(self, num_periods, policy):
    for page in self.page_list:
      page.counts_ep = np.zeros(num_periods)
      page.loc_ep = np.zeros(num_periods)
    self.lru_list = [page.id for page in self.page_list]
    self.policy = policy
    
  def init_tier(self, l1_ratio):
    self.l1_ratio = l1_ratio
    self.l1_pages = int(l1_ratio * self.num_pages)
    idxs = range(self.num_pages)
    if self.l1_ratio == 1:
      self.tier_pages(idxs, [], 0)
    elif self.l1_ratio == 0:
      self.tier_pages([], idxs, 0)
    else:
      l1_tier, l2_tier = [], []
      for i in range(self.num_pages):
        if i % 2 == 0 and len(l1_tier) < self.l1_pages:
          l1_tier.append(i)
        else:
          l2_tier.append(i)
      self.tier_pages(l1_tier, l2_tier, 0)
   
  def tier_pages(self, l1_tier, l2_tier, ep):
    for page_id in l1_tier:
      page = self.page_list[page_id]
      page.loc_ep[ep] = 0
    for page_id in l2_tier:
      page = self.page_list[page_id]
      page.loc_ep[ep] = 1
    
  def update_lru(self, page_id):
    for idx in range(len(self.lru_list)):
      if self.lru_list[idx] == page_id:
        self.lru_list.pop(idx)
        break
    self.lru_list.append(page_id)
   
  def update_tier(self, curr_ep):
    for page in self.page_list:
      page.loc_ep[curr_ep] = page.loc_ep[curr_ep-1]
  
  def get_l2_hot_pages(self, curr_ep, policy):
    # get the l2 hot pages than are HOTTER than the current l1 hot pages
    sorted_hot_page_ids, hot_page_ids, hot_page_cnts = [], [], []
    for page in self.page_list:
      pcnt = 0
      if policy == 'history':
        pcnt = page.oracle_counts_ep[curr_ep - 1]
      elif policy == 'history-touch':
        pcnt = page.oracle_counts_ep[curr_ep - 1]
        if pcnt > 0:
          pcnt = 1
      elif policy == 'oracle':
        pcnt = page.oracle_counts_ep[curr_ep]
      if pcnt != 0: # consider pages that are touched in this period
        hot_page_ids.append(page.id)
        hot_page_cnts.append(pcnt)
    # sort
    sorted_idxs = np.argsort(hot_page_cnts)[::-1]
    sorted_hot_page_ids = [hot_page_ids[i] for i in sorted_idxs]
    if policy == 'history-touch': # go through pages in order
      sorted_hot_page_ids = hot_page_ids
    npages = 0
    page_id = 0
    l2_hot_pages_to_move = []
    while npages < self.l1_pages and npages < len(sorted_hot_page_ids):
      page = self.page_list[sorted_hot_page_ids[page_id]]
      if page.loc_ep[curr_ep-1] == 1:
        l2_hot_pages_to_move.append(page.id)
      npages += 1
      page_id += 1
    return l2_hot_pages_to_move
    
  def get_l1_lru_pages(self, curr_ep):
    lru_page_ids = []
    for page_id in self.lru_list:
      page = self.page_list[page_id]
      if page.loc_ep[curr_ep-1] == 0:
        lru_page_ids.append(page.id)
        
    return lru_page_ids
  
  def capacity_check(self, curr_ep):
    l1_pages = 0
    for page in self.page_list:
      if page.loc_ep[curr_ep] == 0:
        l1_pages += 1
    perc = l1_pages / float(self.num_pages)
    if perc > self.l1_ratio:
      print("ERROR: capacity ratio is ", perc, "instead of", self.l1_ratio)

  def get_page_reuse_histogram(self, num_reqs, bucket_size):
    buckets = range(0, num_reqs, bucket_size)
    num_buckets = len(buckets)
    repeats_per_bucket = np.zeros(num_buckets)
    num_pages_per_bucket = np.zeros(num_buckets)
  
    for page in self.page_list:
      heights, bin_edges = np.histogram(page.reuse_dist, bins=buckets)
      for idx in range(num_buckets - 1):
        if heights[idx] > 1:
          repeats_per_bucket[idx] += heights[idx]
          num_pages_per_bucket[idx] += 1
    avg_repeats_per_bucket = []
    for i in range(num_buckets):
      npages = num_pages_per_bucket[i]
      repeat = repeats_per_bucket[i]
      perc = 0
      if npages != 0:
        perc = repeat / npages
      avg_repeats_per_bucket.append(perc)
    dataX, dataY = [], []
    for idx in range(1, num_buckets):  # exclude the first bucket, its intra period reuse
      if avg_repeats_per_bucket[idx] > 2:
        dataX.append(buckets[idx])
        dataY.append(avg_repeats_per_bucket[idx])
    return dataX, dataY

