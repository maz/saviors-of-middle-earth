require 'yaml'
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

@products=[]
@inputs[:classes].each do |cls|
  @inputs[:per_class].each do |itm|
    itm=itm.clone#SHALLOW copy
    itm[:name]="#{cls} #{itm[:name]}"
    itm[:description]=itm[:description].gsub("$CLASS",cls)
    itm[:reviews]=[]
    @products<<itm
  end
end

@users={}
@random=Random.new(@inputs[:seed])

@five_percent=@products.length/20
@eprod=@products.clone

while @eprod.length>0
  @five_percent.times do
    idx=@random.rand(@eprod.length)
    prod=@eprod[idx]
    @eprod.delete_at idx
    prod[:expiration]=@start_date.strftime
  end
  @start_date+=1
end

def rtween(min,max)
  @random.rand(max-min+1)+min
end

@inputs[:names].each do |name|
  if @products.length==0
    @users[name]=nil
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
      user=@users[@random.rand(@users.length)] while user==name
      review=@inputs[:reviews][@random.rand(@inputs[:reviews].length)]
      product[:reviews]<<{
        :user=>user,
        :rating=>rtween(review[:min],review[:max]),
        :text=>review[:messages][@random.rand(review[:messages].length)]
      }
    end
  end
end

#dump any remaining products on the last user
@users[@inputs[:names].last]+=@products if @products.length>0

File.open(File.join(File.dirname(__FILE__),'fixtures.yaml'),'w') do |f|
  f<<@users.to_yaml
end