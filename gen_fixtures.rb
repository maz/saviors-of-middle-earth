require 'yaml'
require 'json'
require 'date'
require 'time'

@start_date=ARGV[0] ? DateTime.parse(ARGV[0]) : DateTime.now

@inputs=YAML.load_file(File.join(File.dirname(__FILE__),'assets','fixtures','fixture-inputs.yaml'))
def keys_to_symbols(x)
  x.keys.clone.each do |key|
    x[key.to_sym]=x[key]
    x.delete key
  end
  x.values.each do |val|
    if val.kind_of?(Hash)
      keys_to_symbols val
    elsif val.kind_of?(Array)
      val.each{|x| keys_to_symbols(x) if x.kind_of?(Hash) }
    end
  end
end
keys_to_symbols @inputs

@next_itm_id=1

@products=[]
@inputs[:classes].each do |cls|
  @inputs[:per_class].each do |itm|
    itm=itm.clone#SHALLOW copy
    itm[:name]="#{cls} #{itm[:name]}"
    itm[:description]=itm[:description].gsub("$CLASS",cls)
    itm[:avg_rating]=0.0
    itm[:rating_count]=0
    itm[:id]=@next_itm_id
    @next_itm_id+=1
    @products<<itm
  end
end

@users={}
@reviews={}
@random=Random.new(@inputs[:seed])

@five_percent=@products.length/20
@eprod=@products.clone

while @eprod.length>0
  @five_percent.times do
    idx=@random.rand(@eprod.length)
    prod=@eprod[idx]
    @eprod.delete_at idx
    prod[:creation]=@start_date.to_time.utc.to_i
    prod[:price]=Float(@random.rand(10000))/Float(100)
  end
  @start_date-=1
end

def rtween(min,max)
  @random.rand(max-min+1)+min
end

@inputs[:names].each do |name|
  if @products.length==0
    #@users[name]=nil
  else
    @users[name]=[]
    rtween(@inputs[:min_products],@inputs[:max_products]).times do
      break unless @products.length>0
      idx=@random.rand(@products.length)
      @users[name]<<@products[idx]
      @products.delete_at idx
    end
  end
end

@users.each_pair do |name,products|
  next if products.nil?
  products.each do |product|
    rtween(@inputs[:min_reviews],@inputs[:max_reviews]).times do
      user=name
      user=@users.keys[@random.rand(@users.keys.length)] while user==name
      review=@inputs[:reviews][@random.rand(@inputs[:reviews].length)]
      @reviews[user]||=[]
      rating=rtween(review[:min],review[:max])*20
      product[:avg_rating]+=rating
      product[:rating_count]+=1
      @reviews[user]<<{
        :product=>product[:id],
        :rating=>rating,
        :text=>review[:messages][@random.rand(review[:messages].length)]
      }
    end
  end
end
@users.each_pair do |name,products|
  next if products.nil?
  products.each do |prod|
    prod[:avg_rating]=Float(prod[:avg_rating])/Float(prod[:rating_count]) unless prod[:rating_count]==0
  end
end

#dump any remaining products on the last user
@users[@inputs[:names].last]+=@products if @products.length>0

File.open(File.join(File.dirname(__FILE__),'fixtures.json'),'w') do |f|
  f<<JSON.generate({
    :users=>@users,
    :reviews=>@reviews
  })
end